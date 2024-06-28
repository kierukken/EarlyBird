#importing libraries
import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests, feedparser, webbrowser, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import datetime

#splitting the api keys from a file into a list
with open("apiKeys.txt", "r") as file:
    apiKeys = file.readlines()

def getWeather(location, apiKey):
    '''
        This function retrieves the weather data for a given location using the provided API key.

        Parameters
        ----------
        location : str
            The location for which to retrieve the weather data.
        apiKey : str
            The API key to use when making the request.

        Returns
        -------
        dict
            The weather data for the given location.
        '''
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={apiKey}"
    return requests.get(url).json()

def getNews(apiKey, search = None, **kwargs):
    '''
        This function retrieves news data using the provided API key and optional search term.

        Parameters
        ----------
        apiKey : str
            The API key to use when making the request.
        search : str, optional
            The search term to use when retrieving the news data.

        Returns
        -------
        dict
            The news data.
        '''
    if search is not None:
        url = f"{apiKey}&q={search}"
    else:
        url = f"{apiKey}&q=Oakville"
    return feedparser.parse(url)

def configureEvents(newsLabel, link):
    '''
        This function configures events for a given news label and link.

        Parameters
        ----------
        newsLabel : tkinter label object
            The label to configure events for.
        link : str
            The link to open when the label is clicked.

        Returns
        -------
        None
        '''
    #Creates a clickable link for each news article
    newsLabel.bind("<Button-1>", lambda e: webbrowser.open(link))
    #Changes the color of the label when the mouse hovers over it
    newsLabel.bind("<Enter>", lambda e: newsLabel.config(foreground="blue"))
    #Reverts the color of the label when the mouse leaves
    newsLabel.bind("<Leave>", lambda e: newsLabel.config(foreground="black"))

def displayNewsData():
    '''
    This function displays news data in the main window.

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    #Clearing the previous news data
    resetWidget = ttk.Label(mainWindow, font=("Arial", 20), background = "lightblue", justify = 'right')
    resetWidget.place(x=60, y=185, width=700, height=540, anchor="nw")

    #Filtering the search inpnut to remove spaces preventing errors
    searchInput = newsSearchInput.get().replace(' ','',-1)

    #Retrieving the news data and searching if a search input is provided
    if searchInput == "":
        newsData = getNews(apiKeys[1].rstrip())["entries"]
    else:
        newsData = getNews(apiKeys[1].rstrip(), search=searchInput)["entries"]

    #Displaying the news data by looping through the first 11 articles
    for i in range(11):
        #Error handling for when there are no more articles to display
        try:
            # If the title is too long, it is shortened and an ellipsis is added
            if len(newsData[i]['title']) > 65:
                newsData[i]['title'] = newsData[i]['title'][:65] + "..."
            #Creating a label for each article and calling the configureEvents function to make it functional
            newsLabelDisplay = ttk.Label(mainWindow, text=newsData[i]['title'], font=("Arial", 15), background = "lightblue")
            configureEvents(newsLabelDisplay, newsData[i]['link'])
            newsLabelDisplay.place(x=80, y=185+i*50, anchor="nw")
        except:
            #If there are no more articles to display, "No more news to display" is displayed if there are no articles to display and "No results found" is displayed if there are no results for the search input
            if i == 0:
                newsLabelDisplay = ttk.Label(mainWindow, text="No results found", font=("Arial", 15), background = "lightblue")
            else:
                newsLabelDisplay = ttk.Label(mainWindow, text="No more news to display", font=("Arial", 15), background = "lightblue")
            newsLabelDisplay.place(x=80, y=185+i*50, anchor="nw")
            break

def displayStockData(event = None):
    '''
        This function displays stock data for a given event.

        Parameters
        ----------
        event : Event, optional
            The event to display stock data for.

        Returns
        -------
        None
        '''
    #Getting the stock symbol and remove spaces
    stock = stockSearchInput.get().replace(' ','',-1)
    #Getting the time frame set by the user
    time = timeFrame.get()

    #Converting the time frame from str to int for calculations
    if 'Day' in time:
        time = int(time[0])
    elif 'Month' in time:
        time = int(time[0])*30
    elif 'Year' in time:
        time = int(time[0])*365

    #Checks if the stock symbol is empty or the default value and sets it to the last searched stock symbol if it is
    if stock == "" or stock == "EnterStockSymbol":
        stock = open("OldestStock.txt", "r").read()

    #Error handling for when the stock symbol is invalid
    try:
        #Retrieving the stock data and making it into csv
        data = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&interval=30min&outputsize=full&apikey={apiKeys[2].rstrip()}&datatype=csv')
        #Converting the timestamp to datetime and setting it as the index
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)
        #Filtering the data based on the time frame set by the user
        filteredData = data[(data.index >= (datetime.datetime.now() - datetime.timedelta(days=time + 1))) & ((data.index <= datetime.datetime.now() - datetime.timedelta(days=1)))]

        #Creating a surface for the plot
        figure = Figure(figsize=(1, 1), dpi=100)
        #Adding the plot to the surface and setting the title and plotting the points
        plot = figure.add_subplot(1, 1, 1)
        filteredData['close'].plot(ax=plot)
        plot.set_title(f'{stock} Stock Price')

        #Creating a canvas to display the plot and drawing it on the main window
        canvas = FigureCanvasTkAgg(figure, mainWindow)
        canvas.draw()

        #Placing the canvas on the main window
        canvas.get_tk_widget().place(x=1015, y=420, width=380, height=290, anchor="n")

        #Clearing the previous stock data and setting new stock data
        if not (stock == "InvalidStockSymbol/Outofapiuses" and stock == "EnterStockSymbol"):
            with open("OldestStock.txt", "w") as file:
                file.write(stock)
    except:
        #Clearing the previous stock data and setting an error message if the stock symbol is invalid
        if stock != "InvalidStockSymbol/Outofapiuses" and stock != "EnterStockSymbol" and stock != "":
            stockSearchInput.delete(0, "end")
            stockSearchInput.insert(0, "Invalid Stock Symbol/Out of api uses")
        else:
            stockSearchInput.delete(0, "end")
            stockSearchInput.insert(0, "Enter Stock Symbol")

#Creating the main window
mainWindow = tk.Tk()
#Setting the title of the window
mainWindow.title("Early Bird")
#Setting the size of the window
mainWindow.geometry("1280x720")

#Creating the title label
label = ttk.Label(mainWindow, text="Early Bird", font=("Arial", 40))
label.pack()

#Calling the getWeather function to get the weather data for Oakville
weatherData = getWeather("Oakville", apiKeys[0].rstrip())

#Creating the weather label and placing it
weatherLabel = ttk.Label(mainWindow, font=("Arial", 20), background="lightblue", justify = 'right')
weatherLabel.place(x=1015, y=200, width=400, height=250, anchor="center")

#Creating the weather title label and placing it
weatherLabelText =  ttk.Label(mainWindow, text="Oakville", font=("Arial", 20), background = "lightblue")
weatherLabelText.place(x=1015, y=100, anchor="center")

#Creating the weather display labels and placing them
weatherLabelDisplay = ttk.Label(mainWindow, text=f"{round(weatherData['main']['temp']-273.15, 1)}°C", font=("Arial", 20), background = "lightblue")
weatherLabelDisplay.place(x=850, y=150, anchor="w")
weatherLabelDescription = ttk.Label(mainWindow, text=weatherData['weather'][0]['description'], font=("Arial", 20), background = "lightblue")
weatherLabelDescription.place(x=853, y=240, anchor="w")
weatherLabelHigh = ttk.Label(mainWindow, text=f'High: {round(weatherData["main"]["temp_max"]-273.15, 1)}°C', font=("Arial", 15), background = "lightblue")
weatherLabelHigh.place(x=853, y=280, anchor="w")
weatherLabelLow = ttk.Label(mainWindow, text=f'Low: {round(weatherData["main"]["temp_min"]-273.15, 1)}°C', font=("Arial", 15), background = "lightblue")
weatherLabelLow.place(x=1003, y=280, anchor="w")

#Creating the news label and placing it
newsLabel = ttk.Label(mainWindow, font=("Arial", 20), background="lightblue", justify = 'right')
newsLabel.place(x=60, y=76, width=700, height=640, anchor='nw')

#Creating the news title label and placing it
newsLabelText =  ttk.Label(mainWindow, text="News", font=("Arial", 20), background = "lightblue")
newsLabelText.place(x=375, y=76, anchor="nw")

#Creating the search bar
newsSearchInput = ttk.Entry(mainWindow, width=100)
newsSearchInput.place(x=115, y=120, anchor="nw")

#Creating the search button to search for news by calling the displayNewsData function
newsSearchButton = ttk.Button(mainWindow, text="Search", command=displayNewsData, width=10)
newsSearchButton.place(x=650, y=118, anchor="nw")

#Calling the displayNewsData function to display the news data
displayNewsData()

#Creating stock label
stockLabel = ttk.Label(mainWindow, font=("Arial", 20), background="lightblue", justify = 'right')
stockLabel.place(x=1015, y=350, width=400, height=375, anchor='n')
#Creating stock label text
stockLabelText =  ttk.Label(mainWindow, text="Stocks", font=("Arial", 20), background = "lightblue")
stockLabelText.place(x=1015, y=370, anchor="center")
#Creating stock search input and button
stockSearchInput = ttk.Entry(mainWindow, width=40)
stockSearchInput.insert(0, "Enter Stock Symbol")
stockSearchInput.place(x=845, y=390, anchor="nw")
stockSearchButton = ttk.Button(mainWindow, text="Search", width=10, command=displayStockData)
stockSearchButton.place(x=1045, y=388, anchor="nw")
#Creating stock time frame options and selector
timeFrame = tk.StringVar()
timeFrame.set("1 Year")
timeFrameOptions = ttk.OptionMenu(mainWindow, timeFrame, "1 Year", "3 Days", "1 Months", "6 Month", "1 Year", command=displayStockData)
timeFrameOptions.place(x=1130, y=388, anchor="nw")

#Calling the displayStockData function to display the stock data
displayStockData()

#Running the main window
mainWindow.mainloop()
