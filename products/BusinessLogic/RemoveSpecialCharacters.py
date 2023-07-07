
def remove_specialcharacters(string):
    special_chars = "!#$\\%^&*(/).,°–_~\"+:€'`^"
    for special_char in special_chars:
        string = string.replace(special_char, '')
    return string
