#
# Juan Cruz
# CS 341 Project 1 – CTA Database App
# The goal of this project is to write a console-based Python program that inputs
# commands from the user and outputs data from the CTA2 L daily ridership database.
# SQL should be used to retrieve and compute most of the information, while Python is
# used to display the results and if the user chooses, to plot as well
#

import sqlite3
import matplotlib.pyplot as plt


##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    print("General Statistics:")
    
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone();
    print("  # of stations:", f"{row[0]:,}"), # prints the toatl number of stations

    dbCursor.execute("SELECT COUNT(Stop_ID) FROM Stops")
    numStops = dbCursor.fetchone();
    print("  # of stops:", f"{numStops[0]:,}"), # prints the total number of stops

    dbCursor.execute("SELECT COUNT(Station_ID) FROM Ridership")
    numRideEntries = dbCursor.fetchone();
    print("  # of ride entries:", f"{numRideEntries[0]:,}"), # prints the number of ride entries

    dbCursor.execute("SELECT MIN(DATE(Ride_Date)), MAX(DATE(Ride_Date)) FROM Ridership")
    dateRange = dbCursor.fetchone()
    print("  date range:", dateRange[0], "-", dateRange[1]) # prints the date range, from the oldest date to the most recent date in the data base

    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership")
    totalRidership = dbCursor.fetchone()
    print("  Total ridership:", f"{totalRidership[0]:,}") # prints the total number of riders
##################################################################  
    # This method finds all the station names and its Station ID that match the user input #
def command1(dbConn):
    stationNameInput = input("\nEnter partial station name (wildcards _ and %): ") # asks for the station name
    dbCursor = dbConn.cursor() 
    # This sql will return the station id and the station name that matcht the user input
    sqlStationNames = """
            SELECT Station_ID, Station_Name
            FROM Stations
            WHERE Station_Name LIKE ?
            ORDER BY Station_Name ASC
            """
    dbCursor.execute(sqlStationNames, (stationNameInput,)) # executes the sql and gets the input for the sql
    result = dbCursor.fetchall();
    if not result:
        print("**No stations found...")
    else:
        for temp in result:
            print(temp[0], ":", temp[1]) # prints all the result of the sql
##################################################################  
# This method finds the percentage of the riders on weekdays, on Saturday, and on Sunday/holidays for the user station input #
def command2(dbConn):
    analyzeInput = input("\nEnter the name of the station you would like to analyze: ")
    dbCursor = dbConn.cursor()
    sqlAnalyzeStation = """
                        SELECT
                            (SELECT SUM(Num_Riders)
                                FROM Ridership
                                JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                                WHERE Station_Name = ? AND Type_of_Day = 'W') AS weekdayRidership,
                            (SELECT SUM(Num_Riders)
                                FROM Ridership
                                JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                                WHERE Station_Name = ? AND Type_of_Day = 'A') AS SaturdayRidership,
                            (SELECT SUM(Num_Riders)
                                FROM Ridership
                                JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                                WHERE Station_Name = ? AND Type_of_Day = 'U') AS sundayRidership,
                            (SELECT SUM(Num_Riders)
                                FROM Ridership
                                JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                                WHERE Station_Name = ?) AS totalRidership
                        """
    dbCursor.execute(sqlAnalyzeStation, (analyzeInput, analyzeInput, analyzeInput, analyzeInput))
    result = dbCursor.fetchall()
    if not result or result[0][0] is None: # checks if the station input by the user exist
        print("**No data found...")
    else:
        print("Percentage of ridership for the", analyzeInput, "station:")
        for temp in result:
            weekdayRidership = temp[0] # sets the weekly ridership from the sql to a variable for better reading of the code
            saturdayRidership = temp[1] # sets the saturday ridership from the sql to a variable
            sundayRidership = temp[2] # sets the sunday ridership from the sql to a variable
            totalRidership = temp[3] # sets the total ridership from the sql to a variable
            
            print("  Weekday ridership:", f"{weekdayRidership:,}", f"({(weekdayRidership/totalRidership)*100:.2f}%)") # prints the weekly ridership and its percentage
            print("  Saturday ridership:", f"{saturdayRidership:,}", f"({(saturdayRidership/totalRidership)*100:.2f}%)") # prints the saturday ridership and its percentage
            print("  Sunday/holiday ridership:", f"{sundayRidership:,}", f"({(sundayRidership/totalRidership)*100:.2f}%)") # prints the sunday ridership and its percentage
            print("  Total ridership:", f"{totalRidership:,}") # prints the total ridership
##################################################################  
# this method outputs the total ridership on weekdays for each station
def command3(dbConn):
    dbCursor = dbConn.cursor()
    sqlTotalRidership = """
                        SELECT 
                            totalRidership.totalRidership,
                            nameRidership.Station_Name,
                            nameRidership.sumNumRiders
                        FROM
                            (SELECT SUM(Num_Riders) AS totalRidership
                            FROM Ridership
                            JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                            WHERE Type_of_Day = 'W') AS totalRidership,
                            (SELECT Station_Name, SUM(Num_Riders) AS sumNumRiders
                            FROM Ridership
                            JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                            WHERE Type_of_Day = 'W'
                            GROUP BY Station_Name) AS nameRidership
                        ORDER BY sumNumRiders DESC
                        """
    dbCursor.execute(sqlTotalRidership);
    result = dbCursor.fetchall()
    print("Ridership on Weekdays for Each Station")
    for temp in result:
        print(f"{temp[1]} : {temp[2]:,} ({(temp[2]/temp[0])*100:.2f}%)") # prints each of the stations with its total riders
##################################################################  
# this method outputs all the stops for a given line color and direction of the user
def command4(dbConn):
    # print("hello command 4")
    dbCursor = dbConn.cursor()
    colorInput = input("\nEnter a line color (e.g. Red or Yellow): ") # asks for a color input
    colorInput = colorInput.title() # makes the input to be readable in the database eg. from purple-express to Purple-Express
    # sql for the color
    sqlLineColor = """
                    SELECT Lines.Color, Lines.Line_ID
                    FROM Stops
                    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
                    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
                    WHERE Color = ? 
                    """
    dbCursor.execute(sqlLineColor, (colorInput,))
    colorResult = dbCursor.fetchall();
    if not colorResult: # checks for the color if that color line exist
        print("**No such line...")
    else:
        directionInput = input("Enter a direction (N/S/W/E): ") # asks for which direction
        directionInput = directionInput.upper()
        # this sql is for the stop name, direction and if its handicap accesible
        sqlDirection = """
                        SELECT Stop_Name, Direction, ADA
                        FROM Stops
                        LEFT JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
                        LEFT JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
                        WHERE Direction = ? AND Color = ?
                        ORDER BY Stop_Name ASC
                        """
        dbCursor.execute(sqlDirection, (directionInput, colorInput))
        directionResult = dbCursor.fetchall();
        if not directionResult: # checks if the line runs in the direction that the user inputted
            print("**That line does not run in the direction chosen...")
        else:
            for temp in directionResult:
                if temp[2] == 1: # checks for the ADA if it's 1 or 0
                    print(temp[0], ": direction =", temp[1], "(handicap accessible)")
                else:
                    print(temp[0], ": direction =", temp[1], "(not handicap accessible)")

##################################################################  
# this method outputs the number of stops for each, separated by direction
def command5(dbConn):
    print("Number of Stops For Each Color By Direction")
    dbCursor = dbConn.cursor()
    # this sql have multiple selects for the color, direction, stops, and the total stops
    sqlColorStops = """
                    SELECT 
                        groupedStops.Color,
                        groupedStops.Direction,
                        groupedStops.countStops,
                        totalStops.totalStops
                    FROM
                        (SELECT COUNT(Stop_ID) AS totalStops
                        FROM Stops) as totalStops,
                        (SELECT Color, Direction, COUNT(Stops.Stop_ID) AS countStops
                        FROM Stops
                        JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
                        JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
                        GROUP BY Color, Direction
                        ORDER BY Color ASC, Direction ASC) AS groupedStops
                    """
    dbCursor.execute(sqlColorStops)
    result = dbCursor.fetchall();
    for temp in result:
        print(temp[0], "going", temp[1], ":", temp[2], f"({(temp[2]/temp[3])*100:.2f}%)") # prints the desired output
##################################################################
# This command outputs the total ridership for each year for that station by the given station name of the user
def command6(dbConn):
    dbCursor = dbConn.cursor()
    nameInput = input("\nEnter a station name (wildcards _ and %): ") # asks the user for the station name
    sqlRidership = """
                    SELECT
                        numStations.numStations,
                        yearlyRidership.year,
                        yearlyRidership.sumRiders,
                        yearlyRidership.Station_Name
                    FROM
                        (SELECT COUNT(Station_Name) AS numStations
                        FROM Stations
                        WHERE Station_Name LIKE ?) AS numStations,
                        (SELECT strftime('%Y', Ride_Date) AS year, SUM(Num_Riders) AS sumRiders, Station_Name
                        FROM Ridership
                        JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                        WHERE Station_Name LIKE ?
                        GROUP BY year
                        ORDER BY year ASC) AS yearlyRidership
                    """
    dbCursor.execute(sqlRidership, (nameInput, nameInput))
    result = dbCursor.fetchall();
    
    if not result: # checks if the station that was inputted exist
        print("**No station found...")
    elif result[0][0] > 1: # checks if there are multiple stations 
        print("**Multiple stations found...")
    else:
        x = []
        y = []
        stationName = result[0][3]
        print("Yearly Ridership at", stationName)
        for temp in result:
            print(temp[1], ":", f"{temp[2]:,}") # prints the year and the total number of riders in that year
            x.append(temp[1]) # adds the data to the array for the plotting of the graph
            y.append(temp[2])
        plotInput = input("\nPlot? (y/n) ") # asks the user if they want to input it
        plotInput = plotInput.lower() # makes sure that the input 'y' or 'Y' will be valid
        if plotInput == 'y':
            plt.xlabel("Year") # labels the x axis
            plt.ylabel("Number of Riders") # labels the y axis
            plt.title("Yearly Ridership at " + stationName + " Station") # for the title of the graph
            plt.xticks(rotation=45, fontsize=8) # this line changes the font of the x axis label so it's btter to read
            plt.ioff()
            plt.plot(x, y) # plots the data
            plt.show() #shows the graph

##################################################################
# this method outputs the total ridership for each month in that given year and station name by the user
def command7(dbConn):
    dbCursor = dbConn.cursor()
    stationInput = input("\nEnter a station name (wildcards _ and %): ") # for the station name input
    sqlStation = """
                SELECT COUNT(Station_Name), Station_Name
                    FROM Stations
                    WHERE Station_Name LIKE ?
                """
    dbCursor.execute(sqlStation, (stationInput,))
    nameResult = dbCursor.fetchall();
    if not nameResult or nameResult[0][0] == 0: # checks if the station exist
        print("**No station found...")
    elif nameResult[0][0] > 1: # checks if there are multiple stations
        print("**Multiple stations found...")
    else: # if the input is valid
        yearInput = input("Enter a year: ") # asks for the year input
        sqlYear = """
                    SELECT strftime('%m', Ride_Date) AS month, strftime('%Y', Ride_Date) AS year, SUM(Num_Riders)
                    FROM Ridership
                    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                    WHERE Station_Name LIKE ? AND year = ?
                    GROUP BY month
                    ORDER BY month ASC
                    """
        dbCursor.execute(sqlYear, (stationInput, yearInput))
        yearResult = dbCursor.fetchall();
        if not yearResult: # if the year is more than what the data base have ex. 2023
            yearResult = () # it empty outs the year result for graphing

        stationName = nameResult[0][1] # grabs the station name
        print("Monthly Ridership at", stationName, "for", yearInput)
        x = []
        y = []
        for temp in yearResult:
            print(temp[0] + "/" + temp[1], ": " f"{temp[2]:,}") # prints the date and the number of riders in that month
            x.append(temp[0]) # this populates the array for the graph
            y.append(temp[2])
        plotInput = input("\nPlot? (y/n) ")
        plotInput = plotInput.lower()
        if plotInput == 'y':
            plt.xlabel("Month")
            plt.ylabel("Number of Riders")
            plt.title("Monthly Ridership at " + stationName + " Station "  + '(' + yearInput + ')')
            plt.ioff()
            plt.plot(x, y) # plots the data
            plt.show() # shows the graph
##################################################################
# this method outputs the total ridership in that year given by two station names. It can also graphs the data
def command8(dbConn):
    dbCursor = dbConn.cursor()
    yearInput = input("\nYear to compare against? ") # asks ffor the year
    station1Input = input("\nEnter station 1 (wildcards _ and %): ")
    sqlStation1 = """
                SELECT COUNT(Station_Name), Station_Name, Station_ID
                    FROM Stations
                    WHERE Station_Name LIKE ?
                """
    dbCursor.execute(sqlStation1, (station1Input,))
    nameResult1 = dbCursor.fetchall();
    stationName1 = nameResult1[0][1]
    stationId1 = nameResult1[0][2]
    if not nameResult1 or nameResult1[0][0] == 0: # checks if the station exist
        print("**No station found...")
    elif nameResult1[0][0] > 1: # checks for multiple stations
        print("**Multiple stations found...")
    else:
        station2Input = input("\nEnter station 2 (wildcards _ and %): ") # asks for the first station input
        sqlStation2 = """
                SELECT COUNT(Station_Name), Station_Name, Station_ID
                    FROM Stations
                    WHERE Station_Name LIKE ?
                """
        dbCursor.execute(sqlStation2, (station2Input,))
        nameResult2 = dbCursor.fetchall();
        stationName2 = nameResult2[0][1]
        stationId2 = nameResult2[0][2]
        if not nameResult2 or nameResult2[0][0] == 0: # makes sure the station exist
            print("**No station found...")
        elif nameResult2[0][0] > 1:
            print("**Multiple stations found...")
        else:
            sqlAllYear = """
                        SELECT SUM(Num_Riders), strftime('%Y', Ride_Date) AS year
                        FROM Ridership
                        JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                        WHERE Station_Name LIKE ? AND year = ?
                        GROUP BY date(Ride_Date)
                        ORDER BY date(Ride_Date) ASC
                        """
            sqlFirstFive = """
                            SELECT date(Ride_Date) AS date, SUM(Num_Riders) AS dayTotal, strftime('%Y', Ride_Date) AS year
                            FROM Ridership
                            JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                            WHERE Station_Name LIKE ? AND year = ?
                            GROUP BY date
                            ORDER BY date ASC
                            LIMIT 5
                        """
            sqlLastFive = """
                        SELECT date, dayTotal
                        FROM
                            (SELECT date(Ride_Date) AS date, SUM(Num_Riders) AS dayTotal, strftime('%Y', Ride_Date) AS year
                            FROM Ridership
                            JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
                            WHERE Station_Name LIKE ? AND year = ?
                            GROUP BY date
                            ORDER BY date DESC
                            LIMIT 5) AS LastFive
                        ORDER BY date ASC
                        """

            dbCursor.execute(sqlFirstFive, (station1Input, yearInput))
            firstfiveResult = dbCursor.fetchall();
            dbCursor.execute(sqlLastFive, (station1Input, yearInput))
            lastFiveResult = dbCursor.fetchall();
            print("Station 1:", stationId1, stationName1)
            for temp in firstfiveResult: # for the first five days in that year
                print(temp[0], temp[1])
            for row in lastFiveResult: # for the first last days in that year
                print(row[0], row[1])
            
            # same thing the first station does but for station 2
            dbCursor.execute(sqlFirstFive, (station2Input, yearInput))
            firstfiveResult = dbCursor.fetchall();
            dbCursor.execute(sqlLastFive, (station2Input, yearInput))
            lastFiveResult = dbCursor.fetchall();
            print("Station 2:", stationId2, stationName2)
            for temp in firstfiveResult:
                print(temp[0], temp[1])
            for row in lastFiveResult:
                print(row[0], row[1])

            x1, x2, y1, y2 = [], [], [], []
            dbCursor.execute(sqlAllYear, (station1Input, yearInput))
            allYearResult1 = dbCursor.fetchall();
            dbCursor.execute(sqlAllYear, (station2Input, yearInput))
            allYearResult2 = dbCursor.fetchall();
            days = 0
            for temp in allYearResult1: # populates the first array for the first station
                x1.append(days)
                y1.append(temp[0])
                days += 1
            days = 0
            for row in allYearResult2: # populates the second array for the second station
                x2.append(days)
                y2.append(row[0])
                days += 1

            if int(yearInput) > 2021: # checks if the year inputted is valid and in the data base
                nameResult1 = ()
                nameResult2 = ()

            # this lines of code is for graphing
            plotInput = input("\nPlot? (y/n) ")
            plotInput = plotInput.lower()
            if plotInput == 'y':
                plt.xlabel("Day")
                plt.ylabel("Number of Riders")
                plt.title("Ridership Each Day of " + yearInput)
                plt.plot(x1, y1, color='blue', label=stationName1)
                plt.plot(x2, y2, color='orange', label=stationName2)
                plt.legend()
                plt.show()
            
##################################################################   
# this method finds all the station within a square mile radius by the given set of latitude and longitude
def command9(dbConn):
    dbCursor = dbConn.cursor()
    latitudeInput = float(input("\nEnter a latitude: "))

    if not (40 <= latitudeInput <= 43): # checks to make sure the latitude input is within chicago area
        print("**Latitude entered is out of bounds...")
        return

    longitudeInput = float(input("Enter a longitude: ")) # checks to make sure the longitude input is within chicago area
    if not (-88 <= longitudeInput <= -87):
        print("**Longitude entered is out of bounds...")
        return

    # this lines of code calculates the one mile square radius from the user input
    oneMileRight = latitudeInput + round(1/69, 3)
    oneMileLeft = latitudeInput - round(1/69, 3)
    oneMileUp = longitudeInput + round(1/51, 3)
    oneMileDown = longitudeInput - round(1/51, 3)

    sqlRadius = """
            SELECT DISTINCT(Station_Name), Latitude, Longitude
            FROM Stations
            JOIN Stops ON Stations.Station_ID = Stops.Station_ID
            WHERE Latitude BETWEEN ? AND ? AND Longitude BETWEEN ? AND ?
            ORDER BY Station_Name ASC
            """
    
    dbCursor.execute(sqlRadius, (oneMileLeft, oneMileRight, oneMileDown, oneMileUp))
    radiusResult = dbCursor.fetchall();
    x = []
    y = []
    names = []

    if not radiusResult: # makes sure the station exist
        print("**No stations found...")
    else:
        print("\nList of Stations Within a Mile")
        for temp in radiusResult:
            print(f"{temp[0]} : ({temp[1]}, {temp[2]})") #prints the station name and the latitude and longitude
            names.append(temp[0]) # this code is for populating the array for the graph
            y.append(float(temp[1]))
            x.append(float(temp[2]))

        # this lines of code is for graphing
        plotInput = input("\nPlot? (y/n) ")
        plotInput = plotInput.lower()
        if plotInput == 'y':
            image = plt.imread("chicago.png")
            xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # area covered by the map:
            plt.imshow(image, extent=xydims)
            plt.title("Stations Near You")
            plt.plot(x, y)
            for i in range(len(radiusResult)): # this is to show the name in the map in the specific area
                plt.annotate(names[i], (x[i], y[i]))
            plt.xlim([-87.9277, -87.5569])
            plt.ylim([41.7012, 42.0868])
            plt.show()


##################################################################   
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')


print_stats(dbConn)

while True:
    command = input("\nPlease enter a command (1-9, x to exit): ") # asks for which command the user wants
    if command.lower() == 'x':
        exit(0)
    if command == '1': # these lines of code checks for the input
        command1(dbConn)
    elif command == '2':
        command2(dbConn)
    elif command == '3':
        command3(dbConn)
    elif command == '4':
        command4(dbConn)
    elif command == '5':
        command5(dbConn)
    elif command == '6':
        command6(dbConn)
    elif command == '7':
        command7(dbConn)
    elif command == '8':
        command8(dbConn)
    elif command == '9':
        command9(dbConn)
    else:
        print("**Error, unknown command, try again...")
#
# done
#