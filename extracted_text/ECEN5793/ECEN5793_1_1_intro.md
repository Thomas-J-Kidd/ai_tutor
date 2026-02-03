# ECEN5793_1_1_intro.pdf

## Metadata
- **Total Pages**: 18
- **OCR Model**: mistral-ocr-latest
- **Processing Time**: 8.31 seconds
- **Source File**: ECEN5793_1_1_intro.pdf
- **Tokens Used**: N/A

## Document Structure

### Page 1

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content

# ECEN 5793
## Digital Image Processing
Nate Lannan

#### Footer
None

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 2

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Agenda

- Introduce general information about this course
- Introduce Helpful Materials
- Introduce the main projects in this class



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 3

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Course Expectations

## Helpful practices
- Attending the class
- Attending Office Hours (ES 267, WR 1:00-2:30PM)
- Doing projects independently and promptly
- Reading supplementary materials




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 4

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Zoom Access

In-person class attendance is **strongly encouraged**.

- Online attendance via ZOOM (937 4098 0202, Passcode: Image)
- Offline video watching will also be available

All classes will be recorded, and lecture videos will be made available online in Canvas for review.




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 5

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Grading Policy

The final grade is based on
- All six computer projects (85%)
- One student presentation (15%)

The letter grade is based on
- &gt;=90: A
- 80-89: B
- 70-79: C
- 60-69: D
- &lt;60: F



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 6

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Suggested Reading and Prerequisites

## Main Reference

Digital Image Processing 4e

Pearson

Gonzales and Woods

ISBN: 978-0-13-335672-4




## Prerequisites

- ECEN 4763/5763 Digital Signal Processing
- Python background is plus



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 7

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Suggested Reading and Prerequisites

Supplementary References

Deep Learning for Vision Systems

Manning

Mohamed Elgendy

ISBN: 978-1-61-729619-2

Learning OpenCV 4 Computer Vision with Python 3 3e

Packt

Joseph Howse and Joe Minichino

ISBN: 978-1-78-953161-9



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 8

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Suggested Reading and Prerequisites

Supplementary References

https://github.com/kjw0612/awesome-deep-vision#books



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
- https://github.com/kjw0612/awesome-deep-vision#books
- https://github.com/kjw0612/awesome-deep-vision#books
- https://github.com/kjw0612/awesome-deep-vision#books
- https://github.com/kjw0612/awesome-deep-vision#books
- https://github.com/kjw0612/awesome-deep-vision#books

---

### Page 9

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Why do we need images?

One picture is worth more than ten thousand words.

Five senses
- Sight
- Hearing
- Touch
- Taste
- Smell

Often imaging is the interface to computer systems for data that is beyond our sensory perception




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 10

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Digital Image Processing (DIP)

An **image** is defined a two-dimensional function $f(x, y)$

- $x$ and $y$ are spatial (plane) coordinates
- the amplitude $f(x, y)$ of coordinate $(x, y)$ is called intensity or gray level.

A **digital image** is an image when $x, y$, and the amplitude values of $f(x, y)$ are all finite, discrete quantities.

- DIP refers to processing digital images by means of a digital computer.
- **Pixels** are referred to basic image elements which consist an image.

How about a color image?  How about a color video?

$$
f(x, y, c) \text{ where } c = 1, 2, 3
$$

$$
f(x, y, c, t)
$$

2-bit

10-bit




#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 11

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
Outputs of these processes generally are images
Class Outline



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 12

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Image Acquisition


FIGURE 2.15 An example of the digital image acquisition process. (a) Energy ("illumination") source. (b) An element of a scene. (c) Imaging system. (d) Projection of the scene onto the image plane. (e) Digitized image.



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 13

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Image Enhancement





a b c d

## FIGURE 4.30

(a) A chest X-ray image. (b) Result of Butterworth highpass filtering.
(c) Result of high-frequency emphasis filtering.
(d) Result of performing histogram equalization on (c). (Original image courtesy Dr. Thomas R. Gest, Division of Anatomical Sciences, University of Michigan Medical School.)



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 14

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Image Restoration


a b c
d e f
g h i

FIGURE 5.29 (a) Image corrupted by motion blur and additive noise. (b) Result of inverse filtering. (c) Result of Wiener filtering. (d)-(f) Same sequence, but with noise variance one order of magnitude less. (g)-(i) Same sequence, but noise variance reduced by five orders of magnitude from (a). Note in (h) how the deblurred image is quite visible through a "curtain" of noise.



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 15

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Color Image Processing









#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 16

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Morphological Processing







a b c f

FIGURE 9.11

(a) Noisy image.
(c) Eroded image.
(d) Opening of  $A$
(d) Dilation of the opening.
(e) Closing of the opening. (Original image for this example courtesy of the National Institute of Standards and Technology.)



#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 17

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Shape Analysis of Objects











#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING

LECTURE 1. COURSE INTRODUCTION

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

### Page 18

**Dimensions**: {'dpi': 200, 'height': 1500, 'width': 2667}

#### Header
None

#### Main Content
# Shape Representation of Objects






#### Footer
ECEN5793 DIGITAL IMAGE PROCESSING
LECTURE 1. COURSE INTRODUCTION
18

#### Tables
No tables extracted
#### Hyperlinks
No hyperlinks detected

---

