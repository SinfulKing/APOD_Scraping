import nasapy                                       #library provided by NASA's API to get access to the data
import os                                           #to access to folder management
from datetime import date                           #to get access to function to get dates
from dateutil.relativedelta import relativedelta    #same, to get access to relative date 
from PIL import Image                               #image handling
import requests                                     #https requests handler
import csv                                          #format of the data we're gonna use
from io import BytesIO

def get_APOD_data(date, key): #function to fetch data 
    nasa = nasapy.Nasa(key=key)
    try :
        apod = nasa.picture_of_the_day(date=date, hd=True)
        if (apod['media_type']!= 'image'):
            return 1
        return [apod['date'], apod['title'], apod['url']] #return an array with characteristics of a given image
    except :
        return 1


def create_APOD_dataset(start_day, end_day, key, folder):#create the dataset, returning a csv file with col1 for ID(the date), col2 for title and col3 for url
    header=['ID','Date', 'Title']#header for the csv file
    dataset=[]#the array that'll store the data
    with open('APOD_data.csv', mode='w', newline='', encoding='UTF8') as csvfile: #open and create a csv file in writing mode
        writer = csv.writer(csvfile)# create a writer object
        writer.writerow(header)    
    total_days = (end_day-start_day).days#number of total days
    create_folder(folder)#create the folder to store the images
    ID = 1
    for day in range(total_days):
        date = (start_day+relativedelta(days=day)).strftime('%Y-%m-%d') #gets the Nth date and assure it is in YYYY-MM-DD format
        data = get_APOD_data(date, key) #getting the data for this day
        if (data !=1): 
            if (download_image(ID, data[2], 'APOD_images')):#if the image is succesfully downloaded
                dataset.append([ID, data[1]])#add the new data to the end of our array
                print(ID, data)
                with open('APOD_data.csv', mode='a', newline='', encoding='UTF8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([ID, data[0], data[1]])
                ID = ID+1
    return dataset



def download_image(ID, img_URL, folder_name): #download the image and saves it to a folder, the ID being the number of days since the starting date.
    response = requests.get(img_URL)#getting the content of the url
    img = Image.open(BytesIO(response.content))#opens it with PIL library using BytesIO which returns bytes
    width, height = img.size#getting the size of the image to check if we got to modify it
    if(img.format!='PNG' and img.format!='GIF' and img.format!='JPEG'):#acceptable format for the images of the dataset
        return False
    if(width !=256 or height !=256):
        img = img.resize((256,256))#resizing the image while keeping the same relative dimensions
    if(img.mode !='RGB'):
        img = img.convert('RGB')#converting to RGB non JPEG images (e.g most PNGs in RGBA and GIFs in P)
    img.save(f'{folder_name}/{ID}.jpg')#saving the image to given folder
    return True



def create_folder(folder_name): #create folder
    try:
        os.mkdir(folder_name) #create folder with input name
    except:
        return


API_key='ENTER YOUR KEY HERE'#API key from https://api.nasa.gov
starting_date = date(1995, 6, 16)#the first picture published in APOD by Nasa
ending_date = date.today()#current day
data = create_APOD_dataset(starting_date, ending_date, API_key, 'APOD_dataset/APOD_images_data')#creating the dataset, i.e the csv file and downloading the images
