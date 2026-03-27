import java.util.List;
import java.util.ArrayList;

public class Dog extends Animal implements Feedable {
    private String breed;
    private boolean hungry;
    private List<String> tricks;

    public Dog(String name, int age, String breed) {
        super(name, age, "Canine");
        this.breed = breed;
        this.hungry = true;
        this.tricks = new ArrayList<>();
    }

    @Override
    public String makeSound() {
        return "Woof!";
    }

    @Override
    public void feed(String food) {
        if (food == null || food.isEmpty()) {
            throw new IllegalArgumentException("Food cannot be null or empty");
        }
        System.out.println(name + " eats " + food);
        this.hungry = false;
    }

    @Override
    public boolean isHungry() {
        return hungry;
    }

    public void learnTrick(String trick) {
        if (trick != null && !trick.isEmpty()) {
            tricks.add(trick);
            System.out.println(name + " learned: " + trick);
        }
    }

    public String getBreed() {
        return breed;
    }

    public List<String> getTricks() {
        return tricks;
    }
}
