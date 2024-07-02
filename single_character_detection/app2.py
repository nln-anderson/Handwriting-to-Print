# Single character detection app. Run the file and draw a symbol. 

# imports
from torch import nn
import torch.nn.functional as F
import torch
import tkinter as tk
from PIL import Image, ImageOps, ImageDraw
import numpy as np

# Network architecture
class MathNet(nn.Module):
    def __init__(self):
        super(MathNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, kernel_size=5, padding=2)  # 20 filters of size 5x5 with padding
        self.conv2 = nn.Conv2d(20, 40, kernel_size=5, padding=2)  # 40 filters of size 5x5 with padding
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)  # Max pooling with a 2x2 kernel and stride 2
        
        # Define the new fully connected layers
        self.fc1 = nn.Linear(40 * 11 * 11, 400)  # First fully connected layer with 400 neurons
        self.fc2 = nn.Linear(400, 200)  # Second fully connected layer with 200 neurons
        self.fc3 = nn.Linear(200, 80)  # Output layer with 80 classes

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # Apply first convolutional layer, ReLU, and max pooling
        x = self.pool(F.relu(self.conv2(x)))  # Apply second convolutional layer, ReLU, and max pooling
        x = x.view(-1, 40 * 11 * 11)  # Flatten the output for fully connected layers
        x = F.relu(self.fc1(x))  # Apply ReLU activation to the first fully connected layer
        x = F.relu(self.fc2(x))  # Apply ReLU activation to the second fully connected layer
        x = self.fc3(x)  # Output layer
        return x


canvas_size = 200  # Canvas size in pixels
img_size = 45  # Size of the image to match the model input

class Model:
    """
    Backend operations of the application. Includes neural network and any image processing.
    """
    # Instance Vars
    classes: list # contains the labels for the dataset
    image1: Image
    draw: ImageDraw

    # Methods
    def __init__(self) -> None:
        # Initialize instance vars
        self.classes = classes = ['!', '(', ')', '+', ',', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
           '=', 'A', 'C', 'Delta', 'G', 'H', 'M', 'N', 'R', 'S', 'T', 'X', '[', ']', 'alpha', 
           'b', 'beta', 'cos', 'd', 'div', 'e', 'exists', 'f', 'forall', 'forward_slash', 'gamma', 
           'geq', 'gt', 'i', 'in', 'infty', 'int', 'j', 'k', 'l', 'lambda', 'ldots', 'leq', 'lim', 'log', 
           'lt', 'mu', 'neq', 'o', 'p', 'phi', 'pi', 'pm', 'prime', 'q', 'rightarrow', 'sigma', 'sin', 'sqrt', 
           'sum', 'tan', 'theta', 'u', 'v', 'w', 'y', 'z', '{', '}']
        self.network = MathNet()

        # Create an empty image and a drawing object
        canvas_size = 200  # Canvas size in pixels
        img_size = 45  # Size of the image to match the model input
        image1 = Image.new('RGB', (canvas_size, canvas_size), 'white')
        draw = ImageDraw.Draw(image1)
        self.draw = draw
        self.image1 = image1

        # Prepare network
        PATH = './math_net_with_weights_6.pth'
        self.network.load_state_dict(torch.load(PATH))

    def predict(self) -> str:
        """Feeds the input drawing from the UI into the neural network.

        Returns:
            str: Label for predicted output.
        """
        img = self.image1.convert('L')
        img = np.array(img)
        threshold_value = 128
        img = (img > threshold_value) * 255  # Binarize the image
        img = Image.fromarray(img.astype(np.uint8))
        img = self.preprocess(img)
        img = img.unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.network(img)
            predicted_class_idx = torch.argmax(output).item()
            predicted_class_name = self.classes[predicted_class_idx]

        return predicted_class_name

class View(tk.Frame):
    """
    View part of the application. Child of the tk.Frame() class.
    """

    # Instance variables
    canvas: tk.Canvas
    clear_button: tk.Button
    predict_button: tk.Button
    result_label: tk.Label
    draw: ImageDraw

    # Methods
    def __init__(self, parent: tk.Frame, model: Model) -> None:
        super().__init__(parent)
        self.model = model
        self.create_layout()

    
    def create_layout(self) -> None:
        """
        Create the UI layout of the application.
        """
        canvas_size = 200  # Canvas size in pixels
        img_size = 45  # Size of the image to match the model input

        root = tk.Frame()

        # Widgets
        canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg='white')
        canvas.pack()
        self.canvas = canvas

        # Create buttons for clearing and predicting
        clear_button = tk.Button(root, text="Clear")
        clear_button.pack()
        self.clear_button = clear_button
        predict_button = tk.Button(root, text="Predict")
        self.predict_button = predict_button
        predict_button.pack()

        # Create a label to display the prediction result
        result_label = tk.Label(root, text="Draw a symbol and click Predict")
        result_label.pack()
        self.result_label = result_label

class Controller:
    """
    Conencts the controller and the view classes.
    """
    # Instance variables
    model: Model
    view: View

    # Methods
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
    
    # Function to draw on the canvas
    def paint(self, event) -> None:
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.view.canvas.create_oval(x1, y1, x2, y2, fill='black', width=1)  # Pen stroke width reduced
        self.model.draw.line([x1, y1, x2, y2], fill='black', width=2)  # Pen stroke width reduced

    # Function to clear the canvas
    def clear_canvas(self) -> None:
        self.view.canvas.delete("all")
        self.model.draw.rectangle([0, 0, canvas_size, canvas_size], fill='white')

    # Prediction of image
    def predict(self) -> None:
        prediction = self.model.predict()
        self.view.result_label.config(text=f"Predicted: {prediction}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Symbol Recognition")

    model = Model()
    view = View(root, Controller(model, view=None))
    controller = Controller(model, view)
    view.controller = controller

    root.mainloop()