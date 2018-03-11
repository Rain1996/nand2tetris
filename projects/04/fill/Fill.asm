// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)
@KBD
D = M           // get value from keyboard

@i
M = 0

@CLEAR
D; JEQ          // if D == 0 -> clear

(BLACK)
@i
D = M

@8192           // 8k
D = D - A

@LOOP
D; JGE

@i
D = M
@SCREEN         // 16384
A = D + A       // A = i + 16384
M = 1           // set black

@i
M = M + 1       // i = i + 1
@BLACK
0; JMP

(CLEAR)
@i
D = M

@8192           // 8k
D = D - A

@LOOP
D; JGE

@i
D = M
@SCREEN         // 16384
A = D + A       // A = i + 16384
M = 0           // clear

@i
M = M + 1       // i = i + 1

@CLEAR
0; JMP

@LOOP
0; JMP
