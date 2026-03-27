import java.util.List;
import java.util.ArrayList;
import java.util.stream.Collectors;

public class AnimalService {
    private List<Animal> animals;

    public AnimalService() {
        this.animals = new ArrayList<>();
    }

    public void registerAnimal(Animal animal) {
        if (animal == null) {
            throw new IllegalArgumentException("Animal cannot be null");
        }
        animals.add(animal);
        System.out.println("Registered: " + animal.getName());
    }

    public void feedAll(String food) {
        for (Animal animal : animals) {
            if (animal instanceof Feedable) {
                Feedable feedable = (Feedable) animal;
                if (feedable.isHungry()) {
                    feedable.feed(food);
                }
            }
        }
    }

    public Animal findByName(String name) {
        for (Animal animal : animals) {
            if (animal.getName().equals(name)) {
                return animal;
            }
        }
        return null;
    }

    public List<Animal> getAnimalsByType(AnimalType type) {
        List<Animal> result = new ArrayList<>();
        for (Animal animal : animals) {
            if (type == AnimalType.DOG && animal instanceof Dog) {
                result.add(animal);
            } else if (type == AnimalType.CAT && animal instanceof Cat) {
                result.add(animal);
            }
        }
        return result;
    }

    public int getAnimalCount() {
        return animals.size();
    }
}
