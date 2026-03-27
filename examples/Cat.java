public class Cat extends Animal implements Feedable {
    private boolean indoor;
    private int livesLeft;

    public Cat(String name, int age, boolean indoor) {
        super(name, age, "Feline");
        this.indoor = indoor;
        this.livesLeft = 9;
    }

    @Override
    public String makeSound() {
        return "Meow!";
    }

    @Override
    public void feed(String food) {
        System.out.println(name + " eats " + food);
    }

    @Override
    public boolean isHungry() {
        return true;
    }

    public boolean isIndoor() {
        return indoor;
    }

    public int getLivesLeft() {
        return livesLeft;
    }
}
