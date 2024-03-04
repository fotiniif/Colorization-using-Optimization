from tkinter import *
from tkinter import filedialog, colorchooser
from PIL import ImageTk, Image, ImageDraw
import numpy as np
import cv2
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

# main window
root = Tk()
root.title("Colorization using Optimization")

# canvas to display the image
canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=YES)


def open_image():
    global image_path, image, tkimage

    image_path = filedialog.askopenfilename()
    image = Image.open(image_path)
    # convert image to Tkinter-compatible format
    tkimage = ImageTk.PhotoImage(image)
    # display image on canvas
    img_id = canvas.create_image(0, 0, anchor=NW, image=tkimage)
    
    canvas.bind("<Button-1>", lambda event: start_draw(event))
    canvas.bind("<B1-Motion>", lambda event: draw(event))
    
    w, h = image.size
    root.geometry('{}x{}+{}+{}'.format(w, h, (root.winfo_screenwidth() - w) // 2, (root.winfo_screenheight() - h) // 2))

def colorize(image):
    height, width = image.size
    # convert the image to a numpy array
    image = np.asarray(image)

    A = sp.coo_matrix((height*width, height*width))
    b = np.zeros(height*width)

    mean = cv2.blur(image, (3,3))
    m = cv2.blur(image**2, (3,3))
    variance = np.sqrt(m - mean**2)

    for i in range(height):
        for j in range(width):
            idx = i*width + j
            
            data = []
            row = []
            col = []
            # wrs for the neighbors of pixel (i,j)
            for di in range(3):
                for dj in range(3):
                    # out of the image
                    if (i+di < 0 or i+di >= height or j+dj < 0 or j+dj >= width):
                        continue #skip this loop
                    wrs = 1 + ((image[i,j]-mean[i,j])*(image[i+di,j+dj]-mean[i+di,j+dj]))/(variance[i,j]**2)
                    # idx for the neighboring pixel
                    idx2 = (i+di)*width + (j+dj)

                    data.append(wrs) 
                    row.append(idx)
                    col.append(idx2)

                    print("wrs = ", data)
                    print("idx = ", row)
                    print("idx2 = ", col)
                    print("wrs lenth is: ", len(data))
                    print("idx lenth is: ", len(row))
                    print("idx2 lenth is: ", len(col))
                    
                    coo = sp.coo_matrix((data, (row, col)), shape=(height*width, height*width))

                    A += coo[idx, idx2]     
            b[idx] = image[i,j]
            
    U = spsolve(A, b)
    print("U = " + str(U))

    # new numpy array for the colorized image
    color = np.zeros_like(image)
    # Convert color to Tkinter-compatible format and display on canvas for the current block
    color = np.uint8(color)
    tkimage = ImageTk.PhotoImage(image=Image.fromarray(color))

    canvas.create_image(j, i, anchor=NW, image=tkimage)

    # main Tkinter loop
    root.update()

    return color


def start_draw(event):
    global lastx, lasty

    lastx = event.x
    lasty = event.y

def draw(event):
    global lastx, lasty

    x = event.x
    y = event.y
    canvas.create_line((lastx, lasty, x, y), fill=line_color, width=5)
    lastx = x
    lasty = y

    colorize(image)
    # update the Tkinter canvas with the colorized image
    tk_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=tk_image)

def select_color():
    global line_color

    color = colorchooser.askcolor()
    # takes the hexadecimal color as a string
    line_color = color[1]


menu = Menu(root)
file_menu = Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_image)
color_menu = Menu(menu, tearoff=False)
menu.add_cascade(label="Color", menu=color_menu)
color_menu.add_command(label="Select Color", command=select_color)
# add menu on the GUI
root.config(menu=menu)

# start the event loop
root.mainloop()


