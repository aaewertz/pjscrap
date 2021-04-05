import os
from time import strftime
from win32com import client
import re
import utils

def count_files(filetype, folder):
    ''' (str) -> int
    Returns the number of files given a specified file type.
    >>> count_files(".docx")
    11
    '''
    count_files = 0
    for files in utils.get_immediate_files(folder):
        if files.endswith(filetype):
            count_files += 1
    return count_files

if __name__ == "__main__":
    folderName = "downloads"
    filesFolderPath = "files"
      
    print("\n")

    # Look for folders
    dateFolders = utils.get_immediate_subdirectories(folderName)

    # Choose a folder
    choose_text = "Choose folder to transform files to .pdf:\n"

    i = 1
    for folder in dateFolders:
        choose_text += "(" + str(i) + ") " + dateFolders[i-1] + "\n"
        i += 1

    isFolderChooseOk = False
    while not isFolderChooseOk:
        try:
            folder_index = int(input(choose_text))
            choose_folder = os.path.join(folderName, dateFolders[folder_index-1], filesFolderPath)
            isFolderChooseOk = os.path.exists(choose_folder) and os.path.isdir(choose_folder)
        except ValueError or IndexError:
            print("Valor ingresado tiene que ser número entero")
    
    print("The folder choose is: " + choose_folder)
    num_docx = count_files(".docx", choose_folder)
    num_doc = count_files(".doc", choose_folder)

    # Check if the number of docx or doc files is equal to 0 (= there are no files
    # to convert) and if so stop executing the script. 

    if num_docx + num_doc == 0:
        print("\nThe specified folder does not contain docx or docs files.\n")
        print(strftime("%H:%M:%S"), "There are no files to convert. BYE, BYE!.")
        exit()
    else:
        print("\nNumber of doc and docx files: ", num_docx + num_doc, "\n")
        print(strftime("%H:%M:%S"), "Starting to convert files ...\n")

    # Try to open win32com instance. If unsuccessful return an error message.

    try:
        word = client.DispatchEx("Word.Application")
        for files in os.listdir(choose_folder):
            if files.endswith(".docx") or files.endswith(".doc"):
                new_name = re.sub(r"(.doc)|(.docx)", ".pdf", files)
                in_file = os.path.abspath(os.path.join(choose_folder, files))
                new_file = os.path.abspath(os.path.join(choose_folder, new_name))
                doc = word.Documents.Open(in_file)
                print(strftime("%H:%M:%S"), " docx -> pdf ", os.path.relpath(new_file))
                doc.SaveAs(new_file, FileFormat = 17)
                doc.Close()
    except Exception as e:
        print(e)
    finally:
        word.Quit()

    print("\n", strftime("%H:%M:%S"), "Finished converting files.")
