import os
import zipfile
import tempfile

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from services.conversion_service import ConversionService
from apps.history.models import DiagramHistory

service = ConversionService()


class ConvertView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        sources = []

        # Handle file uploads
        files = request.FILES.getlist('files')
        for f in files:
            if f.name.endswith('.java'):
                content = f.read().decode('utf-8', errors='replace')
                sources.append((f.name, content))
            elif f.name.endswith('.zip'):
                sources.extend(self._extract_zip(f))

        # Handle pasted code
        code = request.data.get('code', '').strip()
        if code:
            sources.append(('PastedCode.java', code))

        if not sources:
            return Response(
                {'error': 'No Java source code provided'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = service.convert(sources)

        # Save to history
        if request.user.is_authenticated:
            filenames = ', '.join(fn for fn, _ in sources)
            history_entry = DiagramHistory.objects.create(
                user=request.user,
                filename=filenames[:255],
                source_code='\n\n'.join(f'// {fn}\n{code}' for fn, code in sources),
                class_diagram=result['diagrams'].get('class', ''),
                usecase_diagram=result['diagrams'].get('usecase', ''),
                flow_diagram=result['diagrams'].get('flow', ''),
            )
            result['history_id'] = history_entry.id

        return Response(result)

    def _extract_zip(self, zip_file):
        sources = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(tmp_dir)
                for root, _, files in os.walk(tmp_dir):
                    for fname in files:
                        if fname.endswith('.java'):
                            fpath = os.path.join(root, fname)
                            with open(fpath, encoding='utf-8', errors='replace') as f:
                                sources.append((fname, f.read()))
        return sources


class ExamplesView(APIView):
    def get(self, request):
        example_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'examples'
        )
        if not os.path.isdir(example_dir):
            return Response({'error': 'Examples not found'}, status=404)

        sources = []
        for fname in sorted(os.listdir(example_dir)):
            if fname.endswith('.java'):
                fpath = os.path.join(example_dir, fname)
                with open(fpath, encoding='utf-8') as f:
                    sources.append((fname, f.read()))

        if not sources:
            return Response({'error': 'No example files found'}, status=404)

        result = service.convert(sources)
        return Response(result)
