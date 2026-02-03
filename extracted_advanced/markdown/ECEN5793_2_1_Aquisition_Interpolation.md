# ECEN5793_2_1_Aquisition_Interpolation.pdf

## Metadata
- **Document Type**: pdf
- **Processing Time**: 9.17 seconds
- **Status**: Success
- **Error**: None
- **Pages**: 39
- **Tokens Used**: 0
- **OCR Model**: mistral-ocr-latest

### Additional Metadata

## Document Content

### Page 1

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content

# ECEN 5793
## Digital Image Processing
Nate Lannan

---

### Page 2

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Agenda

- Image acquisition
- Ideal interpolation
- Linear interpolation
- Bicubic interpolation
- Super-resolution



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
2

---

### Page 3

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Questions

Is the human visual system (HVS) telling the truth all the time?
What are the two main issues about digital image acquisition?




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 4

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Review of Eye Structure





#### Footer
LECTURE 3: ACQUISITION AND INTERPOLATION

4

---

### Page 5

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Mach Bands

The HVS tends to undershoot or overshoot around the boundary of regions of different intensities.

a
b
c

FIGURE 2.7
Illustration of the Mach band effect. Perceived intensity is not a simple function of actual intensity.



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 6

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
E C E N 5 7 9 3 D I G I T A L I M A G E P R O C E S S I N G

L E C T U R E 3 : A C Q U I S I T I O N AND I N T E R P O L A T I O N

#### Content
# Visual Illusion

a b c d

FIGURE 2.9 Some well-known optical illusions.





---

### Page 7

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Image Acquisition: Sampling and Quantization


FIGURE 2.15 An example of the digital image acquisition process. (a) Energy (“illumination”) source. (b) An element of a scene. (c) Imaging system. (d) Projection of the scene onto the image plane. (e) Digitized image.



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 8

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Spatial Resolution

Just because an image has high resolution (i.e. pixel count) does not mean it is a quality image.

We need to relate the pixels to spatial units. The image itself does not tell the whole story.

Typical metrics

Printing – dpi, ppi

Imaging – LP/mm

These images have the same pixel count but different spatial resolution




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

8

---

### Page 9

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Example of Sampling

A CCD (Charge-coupled device) camera chip of dimensions 7x7 mm, and having 1024x1024 elements, is focused on a square, flat area, located 0.5m away. How many line pairs per mm will this camera be able to resolve? The camera is equipped with a 35-mm lens.




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
9

---

### Page 10

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Review of Nyquist Theorem





$$
x _ {p} (t) = x (t) p (t)
$$




$$
X _ {p} (j \omega) = \frac {1}{2 \pi} X (j \omega) * P (j \omega)
$$

$x(t)$ is a bandlimited signal

$$
| X (j \omega) | = 0, | \omega | &lt;   \omega_ {M}
$$

$$
P (j \omega) = \frac {2 \pi}{T} \sum_ {k = - \infty} ^ {\infty} \delta (\omega - k \omega_ {s})
$$

$$
\left(\omega_ {s} = \frac {2 \pi}{T}, \text {sampling rate}\right)
$$

$$
\omega_ {s} &gt; 2 \omega_ {M} \rightarrow \text {aliasing free}
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 11

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Two Sampling Conditions







#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

11

---

### Page 12

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Frequency in Images

Spatial frequency has content like time-based signals

High Frequency


Low Frequency


What is the high frequency content and low frequency content in this image?




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
12

---

### Page 13

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Aliasing Problems





#### Footer
LECTURE 2: IMAGING AND PERCEPTION
13

---

### Page 14

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Anti-aliasing pre-filtering before sampling


Original image

Sampling with aliasing

Sampling with anti-aliasing



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

14

---

### Page 15

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content



a b c d e f





a b e d
FIGURE 2.20 (a)  $1024 \times 1024$ , 8-bit image. (b)  $512 \times 512$  image resampled into  $1024 \times 1024$  pixels by row and column duplication. (c) through (f)  $256 \times 256$ ,  $128 \times 128$ ,  $64 \times 64$ , and  $32 \times 32$  images resampled into  $1024 \times 1024$  pixels.

FIGURE 2.20 Typical effects of reducing spatial resolution. Images shown at: (a) 1250 dpi, (b) 300 dpi, (c) 150 dpi, and (d) 72 dpi. The thin black borders were added for clarity. They are not part of the data.



#### Footer
ECENG793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 16

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Quantization

The sampling process requires decision about size $M \times N$, and the quantization process decides the number of gray scales $L$.

Due to the consideration of processing, storage, and sampling hardware, $L$ is typically an integer power of 2:

$$
L = 2^k, \text{ and } f(x, y) \in [0, L - 1]
$$

The number of bits, $b$, required to store a digitized image is

$$
b = M \times N \times k. \qquad b = N^2 k \quad (\text{when } M = N)
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 17

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Number of Gray Levels

The number of gray levels mainly depends on both the contrast ratio (CR) of the environment and the contrast sensitivity about HVS.

[tbl-0.md](tbl-0.md)

$$
\begin{array}{l}
\begin{array}{l}
\boxed{f_{N} = 1 = \frac{(1 + \Delta c)^{N}}{CR} \rightarrow CR = (1 + \Delta c)^{N}} \\
\vdots \\
f_{k+1} = f_{k}(1 + \Delta c) \\
\vdots \\
f_{2} = \frac{(1 + \Delta c)^{2}}{CR} \\
f_{1} = \frac{1 + \Delta c}{CR} \\
f_{0} = \frac{1}{CR} \\
\end{array}
\quad
\begin{array}{l}
\text{Number of gray levels:} \\
N = \frac{\log(CR)}{\log(1 + \Delta c)} \\
\frac{\log(10)}{\log(1.02)} \approx 116.3 \\
\end{array}
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

#### Tables
**Table 1**:

{'id': 'tbl-0.md', 'content': '|   | Contrast sensitivity  |   |   |\n| --- | --- | --- | --- |\n|   |  2% | 1% | 0.5%  |\n|  Contrast ratio |   |   |   |\n|  10\n(office environment) | 116\n(~7 bits) | 231\n(~8 bits) | 462\n(~9 bits)  |\n|  30\n(living room, television) | 172 | 342 | 682  |\n|  100\n(cinema theater) | 232\n(~8 bits) | 463\n(~9 bits) | 923\n(~10 bits)  |', 'format': 'markdown'}

---

### Page 18

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content








#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

18

---

### Page 19

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Interpolation




#### Footer
EGEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
19

---

### Page 20

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Questions

How to resize an image with best quality?

Original low-res image

Nearest neighbor

Bilinear interpolation

Bi-cubic interpolation

Model-based interpolation



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
20

---

### Page 21

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# What is the ideal interpolation?







$$
X _ {r} (j \omega) = X _ {p} (j \omega) H (j \omega)
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 22

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Ideal Interpolation

$$
X _ {r} (j \omega) = X _ {p} (j \omega) H (j \omega) \leftrightarrow x _ {r} (t) = x _ {p} (t) * h _ {i d e a l} (t)
$$




What is the implication here?

Dependency on infinity and non-causality make this not physically realizable



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 23

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Zero-order Hold (ZOH) &amp; Linear Interpolation




#### Footer
LECTURE 3: ACQUISITION AND INTERPOLATION
23

---

### Page 24

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Zooming and Shrinking

Both zooming and shrinking are applied to digital images with two steps
- The creation of new pixel locations
- The assignment of gray levels to those new locations

Pixel Interpolation is the process of using known data to estimate values at unknown locations.
- Nearest neighbor interpolation (ZOH)
- Pixel replication (special case of nearest neighbor interpolation)
- Bilinear interpolation
- Bicubic interpolation

Zooming and shrinking can be done in a similar manner.



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 25

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# How to create new pixel locations?

In the zooming case, when ratio $p$ is not integer, usually new pixels (red points) are created not on the grid.




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

25

---

### Page 26

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Linear Interpolation (1-D)

The 1-D linear interpolator involves a linear model to compute the values of new samples as


$$
d = x ^ {\prime} - x
$$

$$
x = \operatorname {f l o o r} \left(x ^ {\prime}\right)
$$

$$
x + 1 = \operatorname {c e i l} \left(x ^ {\prime}\right)
$$

$$
v \left(x ^ {\prime}\right) = (1 - d) \cdot f (x) + d \cdot f (\hat {x} + 1)
$$

$$
v \left(x ^ {\prime}\right) = (1 - d) f \left(\operatorname {f l o o r} \left(x ^ {\prime}\right)\right) + d \cdot f \left(\operatorname {c e i l} \left(x ^ {\prime}\right)\right)
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 27

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Coordinate System in Matlab




#### Footer
LECTURE 3: ACQUISITION AND INTERPOLATION
27

---

### Page 28

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Coordinate System in numpy




#### Footer
LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 29

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content
# Coordinate swap




#### Footer
LECTURE 3. ACQUISITION AND INTERPOLATION
29

---

### Page 30

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# A crash course in MATLAB

## Image I/O
- imread() – input image
- imwrite() – output image
- imshow() – display image

## Data types for intensity
- im2double() – convert values to double
- im2uint8(), im2uint16() – convert to an unsigned int
- mat2gray() – converts matrix to a gray scale image [0,1]

## Indexing and geometry
- size() – return size of matrix
- ndims() – return number of dimensions of matrix
- meshgrid(), ndgrid() – replication of an array over matrix
- find() – find subscript where condition is satisfied in array
- sub2ind() – convert subscript notation to index

https://www.mathworks.com/help/images/


# MATLAB®



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION
30

#### Hyperlinks
- https://www.mathworks.com/help/images/

---

### Page 31

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# A crash course in a python stack

- Python3 – the more recent the better
- NumPy – library for matrix manipulation
- OpenCV – image I/O and classical computer vision
- Matplotlib – graphing and output image utilities
- scikit-image – image utilities

Simplest install:

- Install python - https://www.python.org/downloads/
- Install pip - https://pip.pypa.io/en/stable/installation/
- Use pip to install libraries (terminal) –
- pip install numpy
- pip install opencv-python
- pip install matplotlib
- pip install scikit-image

import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage

https://docs.opencv.org/
https://numpy.org/doc/stable/
https://matplotlib.org/stable/api/index
https://scikit-image.org/docs/stable/




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 3: ACQUISITION AND INTERPOLATION

#### Hyperlinks
- https://www.python.org/downloads/
- https://pip.pypa.io/en/stable/installation/
- https://docs.opencv.org/
- https://numpy.org/doc/stable/
- https://matplotlib.org/stable/api/index
- https://scikit-image.org/docs/stable/
- https://scikit-image.org/docs/stable/
- https://scikit-image.org/docs/stable/

---

### Page 32

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# A crash course in a python stack

## Image I/O

- cv2.imread() – loads BGR not RGB
- plt.imread()
- skimage.io.imread()
- cv2.imwrite()
- plt.imsave()
- skimage.io.imsave()
- plt.imshow()

## Data types for intensity

- img.astype(np.float64)/max_value – explicit normalization for a double
- (img * 255).astype(np.iint8) – assumes [0,1] for converting to uint
- (img – img.min())/(img.max() – img.min()) – convert any matrix to gray scale

## Indexing and geometry

- A.shape – return size of matrix
- A.ndim – return number of dimensions of matrix
- np.meshgrid(x,y) – replication of an array over matrix
- np.where() – find subscript where condition is satisfied in array
- np.ravel_multi_index((r,c), sz) – convert subscript notation to index




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 33

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Linear Interpolation (2-D)

Bilinear interpolation takes a weighted average of four pixels in the original image to the new pixel.

$$
\begin{array}{l} I (x ^ {\prime}, y ^ {\prime}) \\ = (1 - u) (1 - v) f (\operatorname {f l o o r} \left(x ^ {\prime}\right), \operatorname {f l o o r} \left(y ^ {\prime}\right)) \\ + (1 - u) \cdot v \cdot f (\operatorname {f l o o r} \left(x ^ {\prime}\right), \operatorname {c e i l} \left(y ^ {\prime}\right)) \\ + u \cdot (1 - v) \cdot f (\operatorname {c e i l} \left(x ^ {\prime}\right), \operatorname {f l o o r} \left(y ^ {\prime}\right)) \\ + u \cdot v \cdot f (\operatorname {c e i l} \left(x ^ {\prime}\right), \operatorname {c e i l} \left(y ^ {\prime}\right)) \\ \end{array}
$$

In programming, you have to use either floor(. or ceil(). But don't use them together. Why?




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 34

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Bicubic Interpolation

Bicubic interpolation takes a weighted average of 16 pixels in the original image to the new pixel.

The contribution of each of the 16 neighboring pixels to the new interpolated point is defined by a bicubic function which is related the distance between the new point and each of 16 pixels (the closer distance, the stronger contribution)




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 35

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Bicubic Interpolation (Cont'd)

The interpolation kernel using the Ricker wavelet is given by

$$
h(x) = \begin{cases} 1 - 2|x|^2 + |x|^3 &amp; \text{for } 0 \leq |x| \leq 1 \\ 4 - 8|x| + 5|x|^2 - |x|^3 &amp; \text{for } 1 &lt; |x| \leq 2 \\ 0 &amp; \text{otherwise} \end{cases}
$$



Then the 2D bicubic interpolation is computed as

$$
I(x', y') = \sum_{m=1}^{4} \sum_{n=1}^{4} h(x_m - x') h(y_n - y') f(x_m, y_n)
$$



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

---

### Page 36

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
ECEN5793 DIGITAL IMAGE PROCESSING

#### Content



#### Footer
LECTURE 3: ACQUISITION AND INTERPOLATION
36

---

### Page 37

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Super-resolution vs. Interpolation (1)

Interpolation involves up-sampling the low-resolution image which may not recover sufficient high-frequency components, leading to blurred images.

Super-resolution (SR) involves three major processes: interpolation, deblurring and denoising, leading to more detailed and sharper images.




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

37

---

### Page 38

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Super-resolution vs. Interpolation (2)

Interpolation involves upsampling the low-resolution image which may not recover sufficient high-frequency components, leading to blurred images.

Super-resolution (SR) involves three major processes: interpolation, deblurring and denoising, leading to more detailed and sharper images.




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

38

---

### Page 39

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Content
# Deep Learning for SR

Input


Super Resolution using Keras:
https://github.com/MaokeAl/SRCNN-keras

https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-1.1c9bb5b6cd5

Upcaled nearest neighbour

Upcaled bilinear

Model predication

Ground truth



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 3: ACQUISITION AND INTERPOLATION

#### Hyperlinks
- https://github.com/MaokeAI/SRCNN-keras
- https://github.com/MaokeAI/SRCNN-keras
- https://github.com/MaokeAI/SRCNN-keras
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5
- https://medium.com/data-science/deep-learning-based-super-resolution-without-using-a-gan-11c9bb5b6cd5

---

