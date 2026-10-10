#entorno\scripts\activate - deactivate
#Notes:
 #It must report if some specific Video Id has become "Deleted" or disappeared and what title it used to be
 #implement an option to print the entire play list
 
#import split_playlist_checker # Optional  --> delete this file from the folder!!!

from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import time
import json # for testing
import csv

id_title = {}
match = False
miss = {}
test=0
enter = ''

load_dotenv()

key = os.getenv("API_KEY")

print('API_KEY: '+key)#<<

#Setting the Playlist IDs dictionary
ids = open('Ids\\ids.csv', 'r', newline='', encoding='utf-8')
read_ids = csv.reader(ids)
ids_names = dict(read_ids)
ids.close()

#print(ids_names,'\n\n')#<<

#Swapped dictionary and turning the dict value into list type to later assign a number and path to each playlist ID. This makes the playlist ID more readable by being first item in the csv file
names_ids = {value: [key] for key, value in ids_names.items()}

#Assigning the temp path and a number to each playlist ID
n = 0
for name in names_ids:
    names_ids[name].append('temp\\'+name+'.csv')
    names_ids[name].append('save\\sv_'+name+'.csv')
    names_ids[name].append(n)
    n = n+1
     
    
#for i in names_ids: #<<
#   print(i,names_ids[i]) <<


#--------- Enable the code below -----  #<<


#Extracting playlist to store it in a dictionary var
def extract(id):
    #initializing vars
    global id_title
    id_title = {}
    c=0
    next_p=None
    #key = 'AIzaSyD6YYI-67gvTInOPoFvqJdxXN3D2HSwBWo'#<<
    yt = build('youtube','v3',developerKey=key)

    #extraction request
    print('\nExtracting playlist..', id) 
    while True:
        request = yt.playlistItems().list(
            part ='snippet', 
            pageToken = next_p,
            maxResults = 50, 
            playlistId = id)
                                                                        
        res = request.execute()

        for item in res['items']:
            c = c+1
            id_title[item['snippet']['resourceId']['videoId']] = item['snippet']['title'] #store video id as a key and video title as the value in the id_tittle dictionary
            #print(json.dumps(item['snippet']['resourceId']['videoId'], indent=2)) # to navigate the object for testing
            #print('Id:', item['snippet']['resourceId']['videoId'], '- Title:',item['snippet']['title'], '- '+str(c))
        
        next_p = res.get('nextPageToken')

        if not next_p:
            break
        #print(res)

#Saving current playlist for the next checking or saving a backup of the old playlist depending the on the case
def save(p_temp, p_save, backup=False): #if backup = True as a parameter we will save a copy of save2.csv before it's overwritten by temp2.csv
    tmp = p_temp
    folder = p_save
    
    #If backup == True the goal is just to use the functions to duplicate save2.csv content inside backup folder under a new name
    if backup == True:
         tmp = p_save
         name = input('Name file: ')
         folder = 'backup\\'+name+'.csv' # PENDING?
    
    #opening temp2.csv file to save it in a dict (when by default)
    with open(tmp, 'r', newline='', encoding = 'utf-16') as temp: #to handle csv files newline='' is required 
        read_file = csv.reader(temp)
        temp_data = dict(read_file)

        #copying temp2.csv into save2.csv to save the current playlist for the next comparison (when by default) 
        save = open(folder, 'w', newline='', encoding = 'utf-16') # just anoter method to open a file instead of using with
        copy = csv.writer(save)
        for key, value in temp_data.items():
            copy.writerow([key, value])
        save.close() #when a file is opened without using "with" statement you need to use the "close()" method
         
#Writing the extracted playlist to temp.csv file (overwritting temp)       
def temp(p_temp, p_save):  
    with open(p_temp, 'w', newline='', encoding='utf-16') as temp:
        file = csv.writer(temp)
        for key, value in id_title.items():
            file.writerow([key, value])

    #figuring out if save exist and has content
    if os.path.exists(p_save):
        print('-¬Save File Exists') #if save file already exist it already has content
    else: 
        print("-~Creating Save File")
        save(p_temp, p_save) # if save file doesn't exist it's created now and curent temp content is copied into the created save file

    
#comparison process
def process(play, p_temp, p_save):
    global match
    
    #open saved playlist (previous temp2.csv) to push it into a dictionary
    with open(p_save, 'r', newline='', encoding='utf-16') as saved:
        read_saved = csv.reader(saved)
        saved_dict = dict(read_saved)

        #open current playlist (current temp2.csv) to push it into dictionary  <<< 
        current = open(p_temp, 'r', newline='', encoding='utf-16')
        read_current = csv.reader(current)
        current_dict = dict(read_current)

        #do the comparison where
        for sav_id, sav_title in saved_dict.items():
            for cur_id, cur_title in current_dict.items():
                #print('saved:',sav_id,sav_title,'current:',cur_id,cur_title)
                
                #Titles match (dict values): if titles match, all right, nothing to report
                if sav_title == cur_title: # remvove and test == 1:
                    match = True
                    break 
                #IDs match (dict keys): it's not necessarily ok. Something is odd. Why the title didn't match?    
                elif sav_id == cur_id:
                    match = True
                    miss[sav_id] = [sav_title, cur_title, play]

            #if match remains false after finishing the inner loop that means that item saved_dict was never found in current_dict        
            if match == True:
                match = False
            else:
                miss[sav_id] = [sav_title, 'lost', play]
             
        current.close()
#--X--: Test the function process by removing songs from temp file and create the lost() function to write the miss dict but in .txt format        

#Saving casualties
def loss():
	if miss == {}:
		print('\n<There is nothing to save...>\n')  
	else:	
		nameLost=input('Name of file to Lost>> ')
		with open('bajas\\'+nameLost+'.txt', 'w', encoding='utf-16') as wt :
			for key, value in miss.items():
				wt.write(value[0]+' => '+value[1]+' ~~'+value[2]+'\n')
			


#MENU

def menu(playlist, items): #receiving from  menu(name, names_ids[name])
    playId = items[0]
    pathTemp = items[1]
    pathSave = items[2]

    print('\n\n-------Requesting playlist -------->', playlist,'\n')
    print(pathTemp, pathSave)#<<

    extract(playId)

    #print(f'+++++{playlist} **** {id_title}') #<<  test: is the playlis properli extracted?

    enter = input('\nEnter (or other key) - overwrite temp | S - Skip playlist | X - abort operation: ')

    if(enter == 'x' or enter == 'X'):
        raise BreakOut('Program Aborted..') #Abort entire program
    elif(enter == 's' or enter == 'S'):
        print(f'Skipping {playlist}') # print with placeholder instead of + 
        return True
    else: 
        temp(pathTemp, pathSave)
        input('\nPress Enter to start the playlist checking ( process() )..')#<<
        process(playlist, pathTemp, pathSave)

        #Check if there are changes in the playlists since the last report
        if miss == {}: 
            print(f'\nNO INCIDENCE TO REPORT FOR [ {playlist} ]\n')
        else:
            print('\nºººººººº Report for '+playlist+'\n')
            for key, value in miss.items():
                print(key,'['+value[0]+'] => ['+value[1]+']')

        print('\nThe save folder is about to be updated..\n')

        #Before updating ask if backup or operation abortion is wanted
        enter = input('1 - Backup | 2 - Exit | Enter - Continue : ')
        if enter == '1':
            save(pathTemp, pathSave, backup=True)
        elif enter == '2':
            raise BreakOut('Program Aborted..') #
        
        #Finally the file in folder save must be overwritten automatically by the file from temp folder in order to update it for the next checking
        save(pathTemp, pathSave)




#---------------------------------------- NEW menu ------------------------------------------------ 


print('\n\n~~|<>|-- Current Playlists Available --|<>|~~\n')

#Dyanmically generate a menu printing the name with its assigned number to choose
for name in names_ids:
    print(name,'>>>', names_ids[name][3])

#Type a string with chosen numbers corresponding to the playlist to be tracked 
numbers = input('\nSelect the numbers: ')


hit=False
interrupt = False

#BreakOut is customized exception (child class) that inherites from the standard built-in Exception (parent class)
#All Exceptions are classes in python. We will use this exception to stop both loops from inside of the menu function with a raise statement
class BreakOut(Exception): pass 

#The number matching to a number available in the playlist dictionary is sent to be tracked immediately
try:
    for str_num in numbers:
        for name in names_ids:
            #from that main menu the playlist-ID associated to the chosen number must be sent to the extract function
            #I also need to create a file with the temp paths and add those paths to the dictionary in order to pass it to the functions 
            if int(str_num) == names_ids[name][3]:
                hit=True

                #Sending the name (key) and dictionary items of the selected playlist (value) to the menu function 
                if menu(name, names_ids[name]): break # Functions by default return None. If return True (enter == '2' in menu funtion) Condition == True and break inner loop

except BreakOut as e: # summoning out customized exception.
    print(e) 
    interrupt = True


if hit == False: 
    print('\nNo playlist found. Try again..\n')
elif interrupt == True:
    pass
elif miss == {}:
    print('No playlist data to save ')
else: 
    #------ Report -------
    exit = input('\n(Enter) Save loss - (X) exit without saving: ')

    if exit == 'x' or exit == 'X':
        pass
    else:
         loss()






