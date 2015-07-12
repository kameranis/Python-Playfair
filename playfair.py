"""Title:       Python Playfair
Version:        1.1
Date:           2011-02-11
Description:    A Python implementation of the Playfair cipher.
Author:         Joel Verhagen, Konstantinos Ameranis
Website:        http://www.joelverhagen.com
Licensing:      Do whatever the heck you want with it. Golly, you don't
                even need to credit me if you don't want. Just don't say you
                originally wrote it. That would just make me sad.
"""


import re


class PlayfairError(Exception):
    """Playfair Exception Class"""
    def __init__(self, message):
        super(PlayfairError, self).__init__(message)
        print message


class Playfair(object):
    """Playfair Cipher Class
    Public Api:
        set_password(password)
        encrypt(text)
        decrypt(text)

    If no password is set, throws an error
    """
    omission_rules = [
       'Merge J into I',
       'Omit Q',
       'Merge I into J',
    ]

    def __init__(self, omission_rule=0, double_padding='X',
                 end_padding='X', password=''):
        """omission_rule determines which omission rule you want to use
        (go figure). See the list at the beginning of the constructor
        double_padding determines what letter you would like to use to pad
        a digraph that is double letters
        end_padding determines what letter you would like to use to pad
        the end of an text containing an odd number of letters"""
        if omission_rule >= 0 and omission_rule < len(self.omission_rules):
            self.omission_rule = omission_rule
        else:
            raise PlayfairError('omission_rule values must be between 0 and '
                                + (len(self.omission_rules) - 1))

        self.grid = ''
        self.password = ''
        self.set_password(password)

        self.double_padding = self._check_padding(double_padding, 'double')

        self.end_padding = self._check_padding(end_padding, 'end')

    def _check_padding(self, padding, which_pad):
        """make sure the text for the padding character is valid"""
        if len(padding) != 1:
            raise PlayfairError('The ' + which_pad + ' padding \
must be a single character.')
        elif not self._is_alphabet(padding):
            raise PlayfairError('The ' + which_pad + ' padding must \
be a letter of the alphabet.')
        padding = padding.upper()
        if padding not in self.grid:
            raise PlayfairError('The ' + which_pad + ' padding character \
must not be omitted by the omission rule.')
        return padding

    def _convert_letter(self, letter):
        """returns None if the letter should be discarded,
        else returns the converted letter"""
        if self.omission_rule == 0:
            if letter == 'J':
                letter = 'I'
            return letter
        elif self.omission_rule == 1:
            if letter == 'Q':
                letter = None
            return letter
        elif self.omission_rule == 2:
            if letter == 'I':
                letter = 'J'
            return letter
        else:
            raise PlayfairError('The omission rule provided has not \
been configured properly.')

    def _get_alphabet(self):
        """returns the alphabet used by the cipher
        (takes into account the omission rule)"""
        full_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet = ''

        for letter in full_alphabet:
            letter = self._convert_letter(letter)
            if letter is not None and letter not in alphabet:
                alphabet += letter

        return alphabet

    def _generate_grid(self):
        """generates the 25 character grid based on the omission rule
        and the given password"""
        if self.password is None:
            raise PlayfairError("""No password set. Do not use this function.
Instead use set_password(password)""")
        grid = ''
        alphabet = self._get_alphabet()

        for letter in self.password:
            if letter not in grid and letter in alphabet:
                grid += letter

        for letter in alphabet:
            if letter not in grid:
                grid += letter

        return grid

    def _generate_digraphs(self, text):
        """splits the text text into digraphs"""
        text = self._to_alphabet(text).upper()
        text_fixed = ''

        for i in text:
            letter = self._convert_letter(i)
            if letter is not None:
                text_fixed += letter

        counter = 0
        while counter < len(text_fixed):
            if counter + 1 == len(text_fixed):
                # we have reached the end of the text_fixed
                yield text_fixed[counter] + self.end_padding
                break
            elif text_fixed[counter] != text_fixed[counter + 1]:
                # we just need to create a normal digraph
                yield text_fixed[counter] + text_fixed[counter + 1]
                counter += 2
            else:
                # we have a double letter digraph, so we add the double padding
                yield text_fixed[counter] + self.double_padding
                counter += 1

    def _encrypt_digraph(self, text):
        """encrypts a digraph using the defined grid"""
        if len(text) != 2:
            raise PlayfairError('The digraph to be encrypted must \
be exactly 2 characters long.')
        elif not self._is_upper(text):
            raise PlayfairError('The digraph to be encrypted must contain \
only uppercase letters of the alphabet.')

        first_letter = text[0]
        second_letter = text[1]

        first_letter_pos = self.grid.find(first_letter)
        second_letter_pos = self.grid.find(second_letter)

        first_letter_coords = (first_letter_pos % 5, first_letter_pos / 5)
        second_letter_coords = (second_letter_pos % 5, second_letter_pos / 5)

        if first_letter_coords[0] == second_letter_coords[0]:
            # letters are in the same column
            first_encrypted = self.grid[
                (first_letter_coords[1] + 1) % 5 * 5 + first_letter_coords[0]]
            second_encrypted = self.grid[
                (second_letter_coords[1] + 1) % 5 * 5 + second_letter_coords[0]]

        elif first_letter_coords[1] == second_letter_coords[1]:
            # letters are in the same row
            first_encrypted = self.grid[
                first_letter_coords[1] * 5 + (first_letter_coords[0] + 1) % 5]
            second_encrypted = self.grid[
                second_letter_coords[1] * 5 + (second_letter_coords[0] + 1) % 5]
        else:
            # letters are not in the same row or column
            first_encrypted = self.grid[
                first_letter_coords[1] * 5 + second_letter_coords[0]]
            second_encrypted = self.grid[
                second_letter_coords[1] * 5 + first_letter_coords[0]]

        return first_encrypted+second_encrypted

    def _decrypt_digraph(self, text):
        """decrypts a digraph using the defined grid"""
        if len(text) != 2:
            raise PlayfairError('The digraph to be encrypted \
must be exactly 2 characters long.')
        elif not self._is_upper(text):
            raise PlayfairError('The digraph to be encrypted must contain \
only uppercase letters of the alphabet.')

        first_encrypted = text[0]
        second_encrypted = text[1]

        first_encrypted_pos = self.grid.find(first_encrypted)
        second_encrypted_pos = self.grid.find(second_encrypted)

        first_encrypted_coords = \
                (first_encrypted_pos % 5, first_encrypted_pos / 5)
        second_encrypted_coords = \
                (second_encrypted_pos % 5, second_encrypted_pos / 5)

        if first_encrypted_coords[0] == second_encrypted_coords[0]:
            # letters are in the same column
            first_letter = self.grid[
                    (first_encrypted_coords[1] - 1) % 5 * 5 +
                    first_encrypted_coords[0]]
            second_letter = self.grid[
                    (second_encrypted_coords[1] - 1) % 5 * 5 +
                    second_encrypted_coords[0]]
        elif first_encrypted_coords[1] == second_encrypted_coords[1]:
            # letters are in the same row
            first_letter = self.grid[
                    first_encrypted_coords[1] * 5 +
                    (first_encrypted_coords[0] - 1) % 5]
            second_letter = self.grid[
                    second_encrypted_coords[1] * 5 +
                    (second_encrypted_coords[0] - 1) % 5]
        else:
            # letters are not in the same row or column
            first_letter = self.grid[
                    first_encrypted_coords[1] * 5 + second_encrypted_coords[0]]
            second_letter = self.grid[
                    second_encrypted_coords[1] * 5 + first_encrypted_coords[0]]

        return first_letter+second_letter

    def _to_alphabet(self, text):
        """strips out all non-alphabetical characters from the text"""
        return re.sub('[^A-Za-z]', '', text)

    def _is_alphabet(self, text):
        """tests whether the string only contains alphabetical characters"""
        return not re.search('[^A-Za-z]', text)

    def _is_upper(self, text):
        """tests whether the string contains only \
            uppercase alphabetical characters"""
        return not re.search('[^A-Z]', text)

    def encrypt(self, text):
        """encrypts text"""
        if self.grid is None:
            raise PlayfairError("No password has been specified")
        encrypted_digraphs = []

        for digraph in self._generate_digraphs(text):
            encrypted_digraphs.append(self._encrypt_digraph(digraph))

        return ''.join(encrypted_digraphs)

    def decrypt(self, text):
        """decrypts text"""
        if self.grid is None:
            raise PlayfairError("No password has been specified")
        decrypted_digraphs = []

        for digraph in self._generate_digraphs(text):
            decrypted_digraphs.append(self._decrypt_digraph(digraph))

        return ''.join(decrypted_digraphs)

    def set_password(self, password):
        """sets the password for upcoming encryptions and decryptions"""
        password = self._to_alphabet(password).upper()
        self.password = password
        self.grid = self._generate_grid()
