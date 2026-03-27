public abstract class Animal {
    protected String name;
    protected int age;
    private String species;

    public Animal(String name, int age, String species) {
        this.name = name;
        this.age = age;
        this.species = species;
    }

    public abstract String makeSound();

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public boolean isOlderThan(Animal other) {
        if (other == null) {
            return false;
        }
        return this.age > other.getAge();
    }
}
