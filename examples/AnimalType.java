public enum AnimalType {
    DOG,
    CAT,
    BIRD,
    FISH;

    public String getDescription() {
        switch (this) {
            case DOG:
                return "A loyal companion";
            case CAT:
                return "An independent spirit";
            case BIRD:
                return "A feathered friend";
            case FISH:
                return "An aquatic pet";
            default:
                return "Unknown animal";
        }
    }
}
