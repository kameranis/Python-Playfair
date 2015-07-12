A Python implementation of the Playfair cipher

The Playfair cipher was created by Charles Wheatstone and popularised by Lord Playfair (hence the name).
Playfair is a classic (means not electronic) symmetric cipher (the same key is used for encryption and decryption)
Using a password like "MONARCHY" we get a 5x5 matrix by using at first the distinct letters in our password
and then the rest of the alphabet.

---------------------
| M | O | N | A | R |
---------------------
| C | H | Y | B | D |
---------------------
| E | F | G | I | K |
---------------------
| L | P | Q | S | T |
---------------------
| U | V | W | X | Z |
---------------------

Usually I and J are considered the same letter.
After we split the text in digraphs, if a digraph is the same letter twice, then a double_padding letter is appended.
If the plaintext has an odd number of letters, then an end_padding letter is appended.

If the 2 letters are in the same row, each one is encrypted to the one to its right.
If the 2 letters are in the same collumn, each one is encrypted to the one beneth it.
Else, each letter is encrypted to the letter in the same row, but in the other's collumn

This is a rudimentary implementation of the Playfair cipher in python.
Though not much, it gets the job done, it is beautiful, and scores 9.79/10 in pylint

Modified a warm july evening the day before my graph theory exam.
