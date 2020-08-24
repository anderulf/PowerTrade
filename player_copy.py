# -*- coding: utf-8 -*-
"""

@author: Kasper Emil Thorvaldsen
"""

import sys
#import socket
import json
import time
import select
import random
import math


class InitationPhase():
    
    """
    This class covers the initation phase of the game, in which each player constructs their company and possibly receives a power plan.
    - They will get a fixed starting capital
    - If decided by host, the players will either:
        - Receive a given power plant
        - Receive a power plant of their choice
        - Receive no power plant
    - After that, the player will finish this section    
    
    """
    
    def InitiationPhase(self):
        """
        This function is the main setup for the initiation phase
        - It retrieves data from the host about how the starting conditions are
        - Starting ES is decided and given, starting cash etc.
        - Starting ES can be forced or free of choice, latter must be implemented
        """
        
        
        #Retrieve initial information from host to start this part
        InitData = self.RetrieveData()
        
        #Construct Energy Sources into the game
        self.ConstructES(InitData["ES"])
        
        #Start to fill in data for the player
        self.FillInitData(InitData["Init"])
    
        #Info about ending this phase
        self.FinishInit()
        
        
        #Send confirmation to host that the initation phase is complete
        self.SendData({"Stage":True})
        
        #End InitiationPhase
    
    def ConstructCompany(self):
        """
        This function sets up the important components in the company
        - The most important aspects here are cash, power plants, and results for each round
        """
        
        #Construct Company dictionary
        self.Company            = {}
        
        #State cash variable
        self.Company["Cash"]    = 0
        
        #State Energy sources dictionary for the company
        self.Company["ES"]      = {}
        
        #State dictionary storing power market results
        self.Company["Results"] = {"Profit":0,"Revenue":0,"Cost":0}
        
        #End ConstructCompany
        
    
    def ConstructES(self,ES):
        """Construct the default energy source into the game"""
        
        #Create Energy source dictionary
        self.ES                 = ES
                
        #End ConstructES
        
        

    
    
    def FillInitData(self,InitData):
        """
        This function will register the input data to the company.
        The starting energy source will be set as well, checking for free choice or forced option.
        """
        
        #Register starting capital
        self.Company["Cash"]        = InitData["InitialCash"]
        
        #Information regarding created company, cash given
        self.CompanyCreated()

        #Check if starting energy source is free choice or not
        if InitData["Starting ES"]  == "Free" or InitData["Starting ES"] == "free":
            self.ChooseStartES()
            #Should not be executed now!
            
        #If energy source is existing
        elif InitData["Starting ES"] in self.ES:
            
            while True:
                
                try:
                    #Print info to player about the given power plant
                    self.ForcedInitES(InitData["Starting ES"])
                
                    #Prompt for nickname. No nickname is not allowed!
                    answer = self.GetAnswer("What should the power plant be called?... ")
                    
                    #If the nickname is empty, it will be given a pre-defined nickname
                    if answer == "":
                        
                        #Write to player that no nickname was given
                        self.NoNicknameGiven()
                        
                        #Change nickname to pre-defined
                        answer = "Power"
                        break
                    
                    #If nickname given, no problem here
                    else:
                        break
                    
                #Incase the input gives an error, print error and inform player, and retry
                except Exception as e:
                    self.ErrorMessage(str(e))
                    
                
            #Define name
            name = InitData["Starting ES"]+" 1"
            self.Company["ES"][name]                    = self.ES[InitData["Starting ES"]]
            
            #Some of this is outdated, but whatever :p
            #Set energy source status as active, and register current year in production
            self.Company["ES"][name]["Status"]          = "Active"
            self.Company["ES"][name]["Age"]             = 0
            self.Company["ES"][name]["Upgrading"]       = "None"            
        
            #Ask user for a nickname for the plant
            self.Company["ES"][name]["Nickname"]        = answer
            
            #Print the new power plant in a nice format
            self.PrintNewES(name)

        
        #If the energy source does not exist
        else:
            self.NoESGiven()
            
        #End FillInitData
   
    
    def PrintNewES(self,name):
        Plant = self.Company["ES"][name]
        

        Text = []
        Text.append("Name of Power plant: " + name + ", also known as " + Plant["Nickname"])
        Text.append("")
        Text.append("Energy Source: " + str(name.split()[0]))
        Text.append("")
        Text.append("Classification: " + Plant["Class"])
        Text.append("")
        Text.append("Originl Inv. Cost: " + str(Plant["Investment"]) + " NOK, but you get it for free! Aren't we generous?!")
        Text.append("")
        Text.append("Capacity: " + str(Plant["Capacity"]) + " MW")
        Text.append("")
        Text.append("Efficiency: " + str(Plant["Efficiency"]) + " %, not counting weather effects")
        Text.append("")
        Text.append("Annual Cost: " + str(Plant["Annual cost"]) + " NOK/year")
        Text.append("")
        Text.append("Cost associated with production is based on the market and will be shown later!")
        Text.append("")
        
        self.PrintMenu(Text)
        self.EnterCommand()
        #End PrintNewES
    
    
    def ChooseStartES(self):
        
        
        while True:
            try:
                Text = []
                
                Text.append("You have been given the free choice of choosing your initial power plant.")
                Text.append("The following power plants are available for you:")
                Text.append("")
                
                for plant in self.ES:
                    Text.append(plant + ", capacity = " + str(self.ES[plant]["Capacity"]) + " MW.")
                
                Text.append("")
                Text.append("please note that the cost associated with these will be specified later. The game creator is sorry for this lack in the game.")
                
                Text.append("please write the power plant type you want to start with. Just write the name of the plant")
                
                self.PrintMenu(Text)
                answer = self.GetAnswer("Please write the name of the plant... ")
                
                if answer in self.ES:
                    while True:
                        try:
                
                            #Prompt for nickname. No nickname is not allowed!
                            answer2 = self.GetAnswer("What should the power plant be called?... ")
                    
                            #If the nickname is empty, it will be given a pre-defined nickname
                            if answer2 == "":
                        
                                #Write to player that no nickname was given
                                self.NoNicknameGiven()
                        
                                #Change nickname to pre-defined
                                answer2 = "Power"
                                break
                    
                            #If nickname given, no problem here
                            else:
                                break
                    
                        #Incase the input gives an error, print error and inform player, and retry
                        except Exception as e:
                            self.ErrorMessage(str(e))
                    
                
                    #Define name
                    name = answer +" 1"
                    self.Company["ES"][name]                    = self.ES[answer]
            
                    #Some of this is outdated, but whatever :p
                    #Set energy source status as active, and register current year in production
                    self.Company["ES"][name]["Status"]          = "Active"
                    self.Company["ES"][name]["Age"]             = 0
                    self.Company["ES"][name]["Upgrading"]       = "None"            
        
                    #Ask user for a nickname for the plant
                    self.Company["ES"][name]["Nickname"]        = answer2
            
                    #Print the new power plant in a nice format
                    self.PrintNewES(name)
                    
                    return
            except Exception as e:
                self.ErrorMessage(str(e))
        
        
        #End ChooseStartES
    
    
    #End Class InitationPhase
    
    
class StrategyPhaseClass():
    
    """Class storing execution of the strategy phase"""
    
    def StrategyPhase(self):
        """
        Things done here:
            - Importing strategy phase data
            - Set up an overview over decisions in the strategy phase
            - Make building, upgrading, planning and such available
        """
        
        #Send company information to host
        self.SendData(self.Company)
        
        #Start by importing strategy phase data
        StrtData        = self.RetrieveData()
        
        #Update ES data, as it could have been adjusted from last round
        self.ConstructES(StrtData["Energy Sources"])
        
        #Setup Demand data
        self.StrtDemand(StrtData["Demand"])
        
        #Setup Production Data
        self.StrtProd(StrtData["Production"])
        
        #Get Market info
        self.StrtMarket(StrtData["Market"])
        
        #Declare number of bidding phases
        self.NumBids    = StrtData["BidRounds"]
        
        #Get newsflash info
        self.NewsFlash = StrtData["NewsFlash"]
        
        #Start up User interaction for the strategy phase
        self.StartStrategy()
        
        
        print("Strategy phase done, sending confirmation to host. Wait for all players to finish..")
        self.SendData({"Stage":True})
        #End StrategyPhase
    
    def StrtDemand(self,Demand):
        
        """Expected demand is stored in a self-variable"""
        
        self.DemandData = Demand 
        
        for turn in self.DemandData.copy():
            self.DemandData[int(turn)] = self.DemandData[turn]
        #End StrtDemand
    
    def StrtProd(self,Prod):
        
        """Production expectations for non-dispatchable is stored in a self-variable"""
        
        self.ProdData = Prod      
        for turn in self.ProdData.copy():
            self.ProdData[int(turn)] = self.ProdData[turn]
        #End StrtProd

    def StrtMarket(self,MarketData):
        """
        Store marketdata locally
        """
        
        self.Market = MarketData
        
        #End StrtMarket
        
        
    def StartStrategy(self):
        
        """
        Plan for strategy phase:
            - Short explanation of the strategy phase goals and such
            - Print newsflash from the host
            - Give short list over possible energy sources to purchase (if not round 1)
            - Give list over existing energy sources
            - Menu: option to see either part again
            - Option buy: Choose type -> see info, buy
            - When bought, make buy option unavailable
        """
        
        self.ExplainStrategy()
        
        self.ExplainESClasses()
        
        self.PrintNewsFlash()
        self.EnterCommand()
        
        for plant in self.Company["ES"]:
            self.PrintEnergySource(plant)
        
        if bool(self.Company["ES"]) == False:
            self.NoPlantOwned()
            
        for name in self.ES:
            self.PrintAvailableES(name)
        
        self.MainMenuStrat()

        return
        #End StartStrategy    
    
        
        
    def PrintNewsFlash(self):
        
        """Print the newsflash given """
        
        NewsFlash = self.NewsFlash
        
        self.PrintMenu(NewsFlash)
    
        #End PrintNewsFlash
    
    def PrintEnergySource(self,name):
        
        """
        This function prints important information about each energy source
        """
        
        #Store the plant info locally
        Plant = self.Company["ES"][name]
        
        
        #Text list created for storing data
        Text = []
        
        #name of power plant, and nickname
        Text.append("Name of Power plant: " + name + ", also known as " + Plant["Nickname"])
        
        #Energy source it origins from
        Text.append("Energy Source: " + name.split()[0])
        
        #What class does it go under
        Text.append("Classification: " + Plant["Class"])
        
        #How much did it cost to buy?
        Text.append("Originl Inv. Cost: " + str(Plant["Investment"]) + " NOK")
        
        #The rated capacity
        Text.append("Capacity: " + str(Plant["Capacity"]) + " MW")
        
        #The efficiency not counting weather effects
        Text.append("Efficiency: " + str(Plant["Efficiency"]) + " %, not counting weather effects")
        
        #Annual cost of operation
        Text.append("Annual Cost: " + str(Plant["Annual cost"]) + " NOK/year")
        
        #If dispatchable, the market information must be given
        if Plant["Class"] == "Dispatchable":
            
            #Store market locally
            Market = self.Market[name.split()[0]]

            #Fuel cost
            Text.append("Fuel cost in market: o(x) = " + str(Market["Fuel a"]) + " +" + str(Market["Fuel b"]) + "x NOK/MWh Fuel" )
            
            #CO2 cost
            Text.append("CO2 Cost in market: " + str(Market["CO2 Value"]) + " Nok/MWh power produced")
        
        #If not dspatchable            
        else:
            
            #Marginal cost of operation
            Text.append("Marginal cost [per MWh sold]: " + str(Plant["Marginal cost"]) + " NOK/MWh")
            
            #Weather effects give the following efficiencies
            Text.append("Expected weather efficiency range [0-1]: ")
            
            #For each coming bid round, helps player see excpected performance
            for bid in range(0,self.NumBids):
                
                #Print data for each coming round
                bidData = self.ProdData[bid+1][name.split()[0]]
                Text.append("Bid round " + str(bid+1) + ": Lower: " + str(bidData["Lower"]) + ", Higher: " + str(bidData["Higher"]))
        
        self.PrintMenu(Text)
        self.EnterCommand()
        #End PrintEnergySource
        
    def PrintAvailableES(self,name):
            
        """
        This function prints the available power plants that can be purchased
        """
        #Text list
        Text = []
        
        #give info that this is a available power plant
        Text.append("Available power plant:")
        Text.append("")
        
        #Store plant info locally
        Plant = self.ES[name]
            
        #Energy source it origins from
        Text.append("Energy Source: " + name.split()[0])
            
        #Class type
        Text.append("Classification: " + Plant["Class"])
            
        #Cost to buy
        Text.append("Investment Cost: " + str(Plant["Investment"]) + " NOK")
            
        #rated capacity
        Text.append("Capacity: " + str(Plant["Capacity"]) + " MW")
        
        #Efficiency
        Text.append("Efficiency: " + str(Plant["Efficiency"]) + " %, not counting weather effects")
        
        #Annual cost of operation
        Text.append("Annual Cost: " + str(Plant["Annual cost"]) + " NOK/year")
        
        #If dispatchable, print market info
        if Plant["Class"] == "Dispatchable":
            Market = self.Market[name]
                
            Text.append("Fuel cost in market: o(x) = " + str(Market["Fuel a"]) + " +" + str(Market["Fuel b"]) + "x NOK/MWh Fuel" )
            Text.append("CO2 Cost in market: " + str(Market["CO2 Value"]) + " Nok/MWh power produced")
        
        #if not dispatchable, print marginal cost info and weather effects range
        else:
                
            Text.append("Marginal cost [per MWh sold]: " + str(Plant["Marginal cost"]) + " NOK/MWh")
            
            Text.append("Expected weather efficiency range [0-1]: ")
            for bid in range(0,self.NumBids):
                bidData = self.ProdData[bid+1][name.split()[0]]
                Text.append("Bid round " + str(bid+1) + ": Lower: " + str(bidData["Lower"]) + ", Higher: " + str(bidData["Higher"]))
            
        self.PrintMenu(Text)
        self.EnterCommand()
        
        #End PrintAvailableES
        
    

    def MainMenuStrat(self):
        
        """
        This function takes care of the main menu of the strategy phase
        """
        #At the start, tell that the bought boolean is false, allowing the player to buy a new power plant ONCE
        self.Bought = False
        
        while True:
            try:
                
                #Menu of what to do in this phase                
                self.StratMenu()
                
                #Ask player what to do
                answer = self.GetAnswer("Please write the number of what you want to do... ")
                
                #If needing to see newsflash again
                if answer == "1":
                    
                    self.PrintNewsFlash()
                    self.EnterCommand()
                    
                #if needing to see status on own power plant(s)
                elif answer == "2":
                    
                    for plant in self.Company["ES"]:
                        self.PrintEnergySource(plant)
                        
                    #If no plant exists, tell player that
                    if bool(self.Company["ES"]) == False:
                        self.NoPlantOwned()
                    
                #If wanting to take a look at the purchaseable plants
                elif answer == "3":
                    
                    Text = []
        
                    Text.append("The following power plants are available for purchase:")
        
                    self.PrintMenu(Text)
                    self.EnterCommand()
                    
                    #print each power plant
                    for name in self.ES:
                        self.PrintAvailableES(name)
                
                #If wanting to purchase a power plant
                elif answer == "4":
                    
                    #If have not bought a power plant, this is valid
                    if self.Bought == False:
                        self.PurchaseES()
                        
                    #If already purchased, this will be mentioned to the players
                    else:
                        #Mention that a plant has already been purchased
                        self.AlreadyPurchasedPlant()
                        
                elif answer == "5":
                    
                    #If company has no power plant or have not yet purchased a plant, prompt for a confirmation on this. 
                    if bool(self.Company["ES"]) == False:
                        
                        while True:
                            try:
                                #Explain no plant situation
                                self.InfoNoPlant()
                                
                                #Prompt response
                                answer = self.GetAnswer("Do you want to proceed further?.. ")
                                
                                #if yes, finish phase
                                if answer == "Yes" or answer == "yes" or answer == "y":
                                    return
                                else:
                                    break
                            
                            #If errormessages
                            except Exception as e:
                                self.ErrorMessage(str(e))
                            
                    elif self.Bought == False:
                        while True:
                            try:
                                
                                #Explain no purchase situation
                                self.HaveNotBoughtPlant()
                                
                                #Prompt response
                                answer = self.GetAnswer("Do you want to proceed further?.. ")
                                
                                #if yes, finish phase
                                if answer == "Yes" or answer == "yes" or answer == "y":
                                    return
                                else:
                                    break
                                
                            #if errormessage
                            except Exception as e:
                                self.ErrorMessage(str(e))
                    else:
                        break
            #If error
            except Exception as e:
                self.ErrorMessage(str(e))
                                
                                
        
        #End MainMenuStrat
        
    def PurchaseES(self):
        
        """
        This function sets up so that the player can purchase a power plant if sufficient capital
        """
        
        while True:
            try:
                #Print info about purchaseable power plants
                self.AvailPurchaseES()
            
                #Get answer from playr on what to do
                answer = self.GetAnswer("Write what you want to do... ")
                
                #If first word is info, the player wants info about the power plant
                if answer.split()[0] == "info" or answer.split()[0] == "Info":
                    
                    #If next word is a power plant available
                    if answer.split()[1] in self.ES:
                        
                        #Print info about that power plant
                        self.PrintAvailableES(answer.split()[1])
                
                #If what is written is a valid power plant
                elif answer in self.ES:
                    
                    #Check if available capital exceeds investment cost
                    if self.Company["Cash"] >= self.ES[answer]["Investment"]:
                        
                        while True:
                            try:
                                #Print confirmation information
                                self.ConfirmPurchase(answer)
                                
                                #Ask player to confirm purchase
                                answer2 = self.GetAnswer("Write 'yes' to confirm purchase.. (note, the purchase is irreversible!) ")
                                
                                #If purchase is confirmed
                                if answer2 == "yes" or answer2 == "Yes":
                                    
                                    #Decrease cash
                                    self.Company["Cash"] = self.Company["Cash"] - self.ES[answer]["Investment"]
                                    
                                    #Implement that plant has been bought this round
                                    self.Bought = True
                                    
                                    #Add energy source into the players company
                                    self.AddES(answer)
                                    return
                                
                                #if regret purchase, break out of loop
                                else:
                                    break
                            
                            #if error, print outcome and info
                            except Exception as e:
                                self.ErrorMessage(str(e))
                                break
                        
                    else:
                        
                        #Explain that the purchase is too expensive
                        self.CannotPurchase(answer)
                        
                #If this is written, out of this menu
                elif answer == "back" or answer == "Back":
                    return
                
            #If error, print outcome and info
            except Exception as e:
                self.ErrorMessage(str(e))
                
        
        #End PurchaseES
    
    def AddES(self,ES):
        
        """This function adds a power plant to the company"""
        
        numbering = 0
        
        while True:
            
            #Numbering to increase number if necessary
            numbering = numbering + 1
            
            #Name is type plus number
            name = ES +" " + str(numbering)
            
            #if name exists, this loop must repeat untill it does not
            if name in self.Company["ES"]:
                continue
            
            #if not
            else:
                #Store data in company
                self.Company["ES"][name] = self.ES[ES]
                
                while True:
                    try:
                        #victory screen :p
                        self.BoughtPlant()
                        
                        #Ask for nickname
                        self.Company["ES"][name]["Nickname"] = self.GetAnswer("What should you call the power plant? ")
                        return
                    
                    #if error, repeat is possible
                    except Exception as e:
                        self.ErrorMessage(str(e))
        
        #End AddES

class BiddingPhaseClass():
    
    def BidPhase(self):
        """Function that will setup the bidding phase from start to finish"""
        #print("This will probably not work..")
        
        #Send confirmation to host that this phase has been achieved
        self.SendData({"Stage":True})
        
        #Find number of hours for each bidding phase
        self.bid_duration = math.ceil(8760/self.bidphase)
        
        #Create variable for storing total profit from this round
        self.TotalProfit = 0
        self.TotalCost  = 0
        self.TotalRevenue = 0
        self.SoldBids = 0
        
        #Print initial information regarding bidding phase
        self.WelcomeBidPhase()
        
        for self.turn in range(0,self.bidphase): 
            
            #Define variable for offered energy
            
            #Create bid dictionary
            self.Bids = {}
            
            #Create bid numbering
            self.bid = 0
            
            #Create non-dispatchable production dictionary
            self.NonDisProd = {}
            
            #Fill self.NonDisProd by using this function
            self.PrintInfo()
            
            #Use function to set the production limit on each plant
            self.SetOfferLimits()
            
            #This function will create, delete and take care of the energy bids
            self.AlterBid()
            
            #Send bids to host

            self.SendData({"Bids":self.Bids})
            
            
            
            Text = []
            
            Text.append("Thank you for your bids, they have now been sent to the market.")
            Text.append("")
            Text.append("Now we wait for all players to finish, and to find the market clearing price and your results")
            self.PrintMenu(Text)
            self.EnterCommand()
            
            #Retrieve host results
            self.ResultBids_holder = self.RetrieveData()
            
            #Store the correct results for this player
            self.ResultBids = self.ResultBids_holder[self.Name]
            
            self.GeneralData = self.ResultBids_holder["General"]
            
            #Analyse economical results
            self.AnalyseProfit()
            
            #Send profit results to host
            self.SendData(self.ResNow)
            
            #Text = "The results from this round are: " + str(self.ResNow)
            #self.PrintMessage(Text)
            
            self.PrintBidResults()
            

            
            if self.turn != (self.bidphase-1):
                
                self.NewBidRound()
            
            
        self.FinishBid()
        
        self.Company["Results"]["Profit"] = self.Company["Results"]["Profit"] + self.TotalProfit
        self.Company["Results"]["Cost"] = self.Company["Results"]["Cost"] + self.TotalCost
        self.Company["Results"]["Revenue"] = self.Company["Results"]["Revenue"] + self.TotalRevenue
        
        #End BidPhase
 
    def FinishBid(self):
        
        Text = []
        
        Text.append("The bidding phase is now done, good job!")
        Text.append("")
        Text.append("During this phase, you managed to sell " + str(self.SoldBids)+ " MWh")
        
        Text.append("")
        Text.append("You made a total of " + str(self.TotalProfit) + " NOK, which you can use to further increase the potential of your company!")
        
        self.PrintMenu(Text)
        self.EnterCommand()
    
    
    
    def NewBidRound(self):
        
        Text = []
        
        Text.append("Bidding round " + str(self.turn+1) + " out of " + str(self.bidphase) + " is now complete")
        Text.append("Next round is ready to start!")
        
        self.PrintMenu(Text)
        self.EnterCommand()
        
        #End NewBidRound
    
    def PrintInfo(self):
        """Function that prints actual non-dispatchable production"""
        
        Text = []
        
        Text.append("This is turn " + str(self.turn+1) + " out of " + str(self.bidphase) + ", where each turn consist of " + str(self.bid_duration) + " hours")
        Text.append("")
        Text.append("So the total profits for each MWh for each turn sold will be multiplied by the number of hours the turn consist of.")
        
        Text.append("For this turn, the following can be said about the demand:")
        Text.append("")
        Text.append("Demand is expected to be within " + str(self.DemandData[(self.turn+1)]["Lower"]) + " and " + str(self.DemandData[(self.turn+1)]["Higher"]) + " MWh per hour.")
        Text.append("")
        
        Text.append("As for the non-dispatchable energy sources, the weather effects factor(s) are:")
        
        #For each source, the actual production for this turn is printed
        for source in self.ProdData[self.turn+1]:
            self.NonDisProd[source] = self.ProdData[self.turn+1][source]["Production"]
            Text.append(str(source) + " has a factor of " + str(self.NonDisProd[source]*100) + " %, not including efficiency of the plant")
        
        
        self.PrintMenu(Text)
        self.EnterCommand()
        
        #End PrintInfo

    
    def SetOfferLimits(self):
        
        """Function setting the max production limit for each plant"""
        
        #For each plant owned by the company
        for name in self.Company["ES"]:
            
            #Set offered variable to 0
            self.Company["ES"][name]["Offered"] = 0
            
            #If plant is dispatchable, the maximum production is based on the capacity
            if self.Company["ES"][name]["Class"] == "Dispatchable":
            
                self.Company["ES"][name]["MaxProd"] = self.Company["ES"][name]["Capacity"]
            
            #If plant is non-dispatchable, max production is based on cap, efficiency and current production factor
            else:
                
                self.Company["ES"][name]["MaxProd"] = round(self.Company["ES"][name]["Capacity"]*self.Company["ES"][name]["Efficiency"]*0.01*self.NonDisProd[name.split()[0]],3)
        
        #End SetOfferLimits
    
    def AlterBid(self):
        
        """This function is the menu for what to do during bidding phase"""
        
        #While making bids
        while True:
            
            try:
                
                self.BidMenu()
                answer = self.GetAnswer("Please write the label of the option you wish to perform... ")
                
                
                #Text = "Your options are as follows:"
                #self.PrintMessage(Text)
                
                #Text = "Options: 1- Make bid(s), 2- Delete bid(s),3- See Status, 4- Finish bidding"
                #self.PrintMessage(Text)
                
                #Player writes the option wanted, converted to int value. Error occurs otherwise
                
                #Question = "What do you want to do? Please answer with the correct number"
                #inp = int(self.GetInput(Question))
                
                #inp = int(input("What do you want to do?\n"))
                
                #If wanting to create a bid
                if answer == "1":
                    self.CreateBid()
                    
                #If wanting to delete an existing bid
                elif answer == "2":
                    self.DeleteBid()
                    
                #If wanting an overview of the current bids
                elif answer == "3":
                    self.PrintBids()
                    self.PrintLeftEnergy()
                    
                #If wanting to exit
                elif answer == "4":
                    return
                
                #If an invalid option was written

            
            #This occurs if something caused an error, asking the player to try again
            except Exception as e:
                self.ErrorMessage(str(e))
            
        #End AlterBid    
    
    def CreateBid(self):
        """
        This function will create a bid based on the users energy sources
        """
        
        self.PrintBids()
        self.PrintLeftEnergy()
        
        while True:
            try:
                #Print bids and leftover energy

                self.CurrentBid = {}
                
                Text = []
                
                Text.append("You wish to create a new bid.")
                Text.append("")
                
                Text.append("So far, each power plant has the following power distribution:")
                
                for name in self.Company["ES"]:
                
                    plant = self.Company["ES"][name]
                    
                    Text.append("The plant " + name + " has a total capacity of " + str(plant["MaxProd"]) + " MWh, and has offered " + str(plant["Offered"]) + " MWh so far")
                    Text.append("Thus, it has " + str(plant["MaxProd"]-plant["Offered"]) + " MWh left that could be sold")
                    
                    Text.append("")
                
                
                Text.append("To make a bid, you must name the name of the plant you wish to offer from (ex. 'Gas 1')")
                Text.append("To exit, please write 'back' to exit to last menu!")
                
                self.PrintMenu(Text)
                
                answer = self.GetAnswer("Write the number of the plant you wish to sell energy from... ")
                
                #If this plant exists in the companys list
                if answer in self.Company["ES"]:
                    
                    plant = self.Company["ES"][answer]
                    #print("makebid")
                    
                    
                    
                    while True:
                        try:
                            Text = []
                            
                            Text.append("You want to create a bid from plant " + answer)
                            
                            
                            #Ask the player to specify energy quantity to sell
                            Text.append("This plant has a remainder of " + str(plant["MaxProd"]-plant["Offered"]) + " MWh left to sell")
                            Text.append("")
                            Text.append("You will need to specify both the energy amount and the price.")
                            Text.append("As always, write 'back' to exit this!")
                            self.PrintMenu(Text)
                            
                            energy = self.GetAnswer("How much energy do you want to sell? To sell remainder write 'rem'... ")
                            
                            
                            #If quantity equals rem, the remaining energy is specified
                            if energy == "rem" or energy == "Rem"   :
                                energy = plant["MaxProd"]-plant["Offered"]
                                break
                            
                            #If player wants to abort this
                            elif energy == "back" or energy == "Back":
                                return
                            
                            #If not, the energy specified will be analyzed
                            
                            elif float(energy) <= 0:
                                self.ErrorMessage("You wrote a negative power amount or 0, this is not accepted!")
                            
                            else:
                                #Convert to float. If a word is written, an error will occur making it loop back to start
                                energy = float(energy)
                                
                                #If energy is less or equal to available quantity, it is okay
                                if energy <= (plant["MaxProd"]-plant["Offered"]):
                                    break
                                else:
                                    Text = []
                                    Text.append("Sadly, the specified amount is higher than the available power. You would get into trouble if this would go through, the government does not like this stuff. Luckily, we stopped you now ;)")
                                    
                                    self.PrintMenu(Text)
                                    self.EnterCommand()
            
                        #If error occurs, the error is printed, and the setup will retry the attempt
                        except Exception as e:
                            self.ErrorMessage(str(e))
                    
                    
                    #Store the quantity
                    self.CurrentBid["Energy"] = energy
                    
                    #Setup for getting price from player
                    while True:
                        try:
                            
                            Text = []
                            
                            Text.append("Thanks for the input, you have offered a total of " + str(self.CurrentBid["Energy"]) + " MWh")
                            Text.append("")
                            
                            Text.append("Now, please specify the price for this bid (or write 'back' to exit)")
                            
                            self.PrintMenu(Text)
                            
                            price = self.GetAnswer("Please write the price for this energy bid (per MWh)... ")
                            
                            if price == "back" or price == "Back":
                                return
                            #Store the price value as a float. If a word, error will prevent it from being stored and a retry will occur
                            self.CurrentBid["Price"] = float(price)
                            break    
                        
                        #If error, printing error and specify what to do. A retry will happen
                        except Exception as e:
                            self.ErrorMessage(str(e))
                        
                    #Write the efficiency of the class, mainly for dispatchable units
                    self.CurrentBid["Eff"] = plant["Efficiency"]
                    
                    #Note Type of bid (PV, Gas etc)
                    self.CurrentBid["Type"] = answer.split()[0]
                    
                    #Note the origin plant the bid is from
                    self.CurrentBid["Origin"] = answer
                    
                    #Update amount offered from this plant
                    plant["Offered"] = plant["Offered"] + energy
                    
                    #Store the bid in the accumulated dictionary
                    self.Bids[self.bid] = self.CurrentBid
                    
                    #Update bid number
                    self.bid = self.bid + 1
                    
                #If this is valid, the user wants to return
                elif answer == "back" or answer == "Back":
                    return


            except Exception as e:
                self.ErrorMessage(str(e))
        #End CreateBid

    def PrintLeftEnergy(self):
        #print("heisan")
        """
        Function that shows the remaining power capacity of each plant"
        """
        #For each plant
        
        Text = []
        for name in self.Company["ES"]:
            
            plant = self.Company["ES"][name]
            
            

            
            Text.append("The plant " + name + " has a total capacity of " + str(plant["MaxProd"]) + " MWh, and has offered " + str(plant["Offered"]) + " MWh so far")
            Text.append("Thus, it has " + str(plant["MaxProd"]-plant["Offered"]) + " MWh left that could be sold")
            
            Text.append("")
            
            #Print plant information about available energy sales
            #print("Plant",name,"has a total capacity of",str(plant["MaxProd"]),"\n has offered",str(plant["Offered"]),"\n and have remaining",str(plant["MaxProd"]-plant["Offered"]))
            
            if plant["Class"] == "Non-dispatchable":
                
                Text.append("Also, the marginal cost for this plant is: " + str(plant["Marginal cost"]))

            elif plant["Class"] == "Dispatchable":
                
                name2 = name.split()[0]
                if name2 in self.Market:
                    fuel_a = self.Market[name2]["Fuel a"]
                    fuel_b = self.Market[name2]["Fuel b"]
                    CO2 = self.Market[name2]["CO2 Value"]
                    
                    
                    Text.append("Also, this plant has a marginal cost for fuel equivalent to: Fuel(x) = " + str(fuel_a) + " + " + str(fuel_b) + "x NOK/MWh, where x is the amount of fuel used by all participants!")
                    Text.append("")
                    Text.append("Cost for CO2 is " + str(CO2) + "x NOK/MWh, where x is right now the amount of MWh produced")
            
            Text.append("")
            Text.append("")
        
        self.PrintMenu(Text)
        self.EnterCommand()
            
        #End PrintLeftEnergy
    
    def PrintBids(self):
        
        """Function printing the current bids created. Bid number, quantity, price and origin included"""
        
        
        Text = []
        
        
        Text.append("You have currently offered the following bids:")
        Text.append("")
        
        #For each bid, print the bid with relevant data
        for bid in self.Bids:
            currBid = self.Bids[bid]
            Text.append("Bid " + str(bid) + ", Energy: "+ str(currBid["Energy"]) + " MWh, Price: " + str(currBid["Price"]) + " NOK/MWh, Origin: "+ str(currBid["Origin"]))
            #Text = "Bid " + str(bid) + ", Energy: "+ str(currBid["Energy"]) + ", Price: " + str(currBid["Price"]) + ", Origin:"+ str(currBid["Origin"])
            #self.PrintMessage(Text)
            
            #print("Bid",str(bid),"Energy:",currBid["Energy"],", Price",currBid["Price"],", Origin",currBid["Origin"],"\n")

        
        self.PrintMenu(Text)
        self.EnterCommand()
        #End PrintBids


    def DeleteBid(self):
        """
        This function will delete an existing bid.
        The free energy will be connected to the correct energy source to allow redistributing the energy
        """
        
        while True:
            try:
                #Print the current bids
                Text = []
                
                Text.append("You are trying to delete one of your existing bids")
                Text.append("")
                
                Text.append("You have currently offered the following bids:")
                Text.append("")
        
                #For each bid, print the bid with relevant data
                for bid in self.Bids:
                    currBid = self.Bids[bid]
                    Text.append("Bid " + str(bid) + ", Energy: "+ str(currBid["Energy"]) + " MWh, Price: " + str(currBid["Price"]) + " NOK/MWh, Origin: "+ str(currBid["Origin"]))
                
                #Ask user to specify bid to delete
                
                Text.append("Do delete a bid, you must write down the bid number. Example: '0' will delete bid 0. The locked energy will be freed up so the energy can be put into a new bid.")
                Text.append("")
                Text.append("To go back, please write 'back'")
                
                self.PrintMenu(Text)
                
                answer = self.GetAnswer("What bid should be deleted? Write bid number... ")
                
                #inp = input("What bid should be deleted? Write bid number (write 'back' to go back)")
                
                
                #If this occurs, the user wants to abort deleting
                if answer == "back" or answer == "Back":
                    return
                
                #If the bid number exists, go forward
                elif int(answer) in self.Bids:
                    
                    answer = int(answer)
                    #store locally bid energy and origin
                    bid = self.Bids[answer]
                    energy = bid["Energy"]
                    Type = bid["Origin"]
                    
                    #If the plant exists
                    if Type in self.Company["ES"]:
                        
                        #Offered energy from this plant will be increased by the value of the bid
                        plant = self.Company["ES"][Type]
                        plant["Offered"] = plant["Offered"]- energy
                    
                    #Bid is deleted from the dictionary
                    del(self.Bids[answer])
                    
                    
                    Text = []
                    Text.append("The bid has been successfuly deleted!")
                    Text.append("The energy has been returned to the proper power plant")
                    
                    self.PrintMenu(Text)
                    self.EnterCommand()
                
                #If this occurs, the bid number does not exist, and the user should try again
                else:
                    
                    Text = []
                    
                    Text.append("The bid number you wrote gave no result, please try again or write 'back' to exit the menu!")
                    self.PrintMenu(Text)
                    
                    self.EnterCommand()
                    
                    
            except Exception as e:
                self.ErrorMessage(str(e))
                
        #End DeleteBid
            


    
    def PrintBidResults(self):
        bids = self.ResultBids["Bids"]
        
        Text = []
            
        Text.append("Congratulations (for us the market), the market has been cleared!")
        Text.append("")
        Text.append("For this turn, the demand was cleared at " + str(self.DemandData[self.turn+1]["Demand"]))
        #Text.append("(maybe insert more interesting data, like marketshare and such?")
        
        Text.append("")
        Text.append("The systemprice for the market ended at " + str(self.GeneralData["Systemprice"]) + " NOK/MWh")
        
        if self.GeneralData["Rationing"] == True:
            Text.append("")
            Text.append("The market sadly suffered from low power contribution and few cheap offers, where rationing had to be initialized")
            Text.append("")
            Text.append("The community managed to ration about " + str(self.GeneralData["P_rat"]) + " MWh.")
        
        else:
        
            Text.append("")
            Text.append("The market received bids equivalent to " + str(self.GeneralData["P_off"]) + " MWh, which in total could cover " + str(self.GeneralData["P_off_frac"]) + " % of total demand")
            
        Text.append("")
        Text.append("The marketshare for each energy source has been revealed to be:")
        Text.append("")
        
        for source in self.GeneralData["Marketshare"]:
            Text.append("The energy source " + source + " had a total share of " + str(self.GeneralData["Marketshare"][source]) + " % of total demand")
            
        
        self.PrintMenu(Text)
        self.EnterCommand()
        
        Text = []

        Text.append("In terms of bids you offered, this is your result. Do note that the systemprice of " + str(self.GeneralData["Systemprice"]) + " NOK/MWh is what you get for your sold bids!")
        Text.append("")
        #For each bid
        for bid in bids:
            
            Text.append("Bid " + str(bid) + ", from " + bids[bid]["Type"] + " Had an offer of " + str(bids[bid]["Energy"]) +" MWh for " + str(bids[bid]["Price"]) +" NOK/MWh, inwhich " + str(bids[bid]["Sold"]) + " MWh got sold")
            
            
        Text.append("")
        Text.append("Your company had these results for this round in terms of profit:")
        Text.append("")
        
        Text.append("Your revenue for this turn was " + str(self.ResNow["Revenue"]) + " NOK")
        Text.append("Your cost for this turn was " + str(self.ResNow["Cost"]) + " NOK")
        Text.append("Your profit for this turn was " + str(self.ResNow["Profit"]) + " NOK")
        
        Text.append("")
        
        Text.append("Your company has for this bidding phase made a total profit of " + str(self.TotalProfit) + " NOK.")
        Text.append("Your company has for this bidding phase has made a total revenue of " + str(self.TotalRevenue) + " NOK.")
        Text.append("Your company has for this bidding phase has had a total cost of " + str(self.TotalCost) + " NOK.")
        
        
        
            
        self.PrintMenu(Text)
        self.EnterCommand()
            
        #End PrintBidResults
        
    
    def AnalyseProfit(self):
        
        """This function will find the revenue, cost and profit gained from this bidding round"""
        
        #Create economical analysis dictionary
        self.ResNow = {"Revenue":0,"Cost":0,"Profit":0}
        
        #Store systemprice variable
        self.SystemPrice = self.ResultBids["Systemprice"]
        
        #Find revenue gains from this round
        self.FindRevenue()
        
        #Find costs from this round
        self.FindCost()
        
        #Find Profit from this round
        self.ResNow["Profit"] = self.ResNow["Revenue"]-self.ResNow["Cost"]
        
        self.TotalProfit = self.TotalProfit + self.ResNow["Profit"]
        self.TotalCost = self.TotalCost + self.ResNow["Cost"]
        self.TotalRevenue = self.TotalRevenue + self.ResNow["Revenue"]
        
        #End AnalyseProfit
    
    def FindCost(self):
        
        """This function finds the cost for each plant, based on production"""
        
        #Create cost variable
        Cost = {}
        TotalCost = 0
        
        #For all registered ES in the company
        for name in self.Company["ES"]:
            plant = self.Company["ES"][name]
            CostES = {}
            
            #Find annual cost for this time period (based on rounds)
            CostES["Annual"] = plant["Annual cost"]/self.bidphase
            
            SumProd = 0
            #Find all bids that are connected to this plant. Accumulate production
            for bid in self.ResultBids["Bids"]:
                if self.ResultBids["Bids"][bid]["Origin"] == name:
                    SumProd = SumProd + self.ResultBids["Bids"][bid]["Sold"]
            
            #If dispatchable, CO2 and Fuel must be taken into consideration
            if plant["Class"] == "Dispatchable":
                
                #Cost of CO2 per MWh
                CO2 = plant["CO2 emission"]*self.ResultBids["CO2 Cost"][name.split()[0]]
                
                #Cost of Fuel per MWh produced, based on total fuel sold
                Fuel = self.ResultBids["Fuel Cost"][name.split()[0]]/(plant["Efficiency"]*0.01)
                
                #Total cost for the operational costs, including #hours
                
                #HERE IT IS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                CostES["Marginal"] = CO2 + Fuel
                CostES["Total_Marg"] = (CO2 + Fuel)*SumProd*self.bid_duration
                
                
            #If non-dispatchable, the cost is marginal cost*prod*duration
            else:
                CostES["Marginal"] = plant["Marginal cost"]
                CostES["Total_Marg"] = plant["Marginal cost"]*SumProd*self.bid_duration
            
            #Total cost for this is the annual pluss operational (here named marginal)
            
            Text = "Plant " + name + " had a marginal cost of " + str(CostES["Marginal"])+ " NOK/MWh sold"
            self.PrintMessage(Text)

            Cost[name] = CostES["Annual"] + CostES["Total_Marg"]
            
            #Accumulate all costs
            TotalCost = TotalCost + Cost[name]
        
        #Store totl cost
        self.ResNow["Cost"] = TotalCost
            
        #End FindCost
    
    def FindRevenue(self):
        
        """This function finds the total revenue from all the bids"""
        
        #Store bids in local variable
        bids = self.ResultBids["Bids"]
        Revenue = 0
        
        #For each bid
        for bid in bids:
            
            #Store energy sold
            Energy = bids[bid]["Sold"]
            
            #Total revenue is accumulated by energy sold, systemprice and #hours
            Revenue = Revenue + Energy*self.SystemPrice*self.bid_duration
            
            self.SoldBids = self.SoldBids + Energy
            
        #Store total revenue
        self.ResNow["Revenue"] = Revenue

        #End FindRevenue

    
    

    
    
    
    #End Class BiddingPhaseClass


    
class EndGameClass():
    
    def EndGame(self):
        
        Text = []
        
        Text.append("Congratulations " + self.Name + ", you have now completed the game!")
        
        Text.append("")
        Text.append("I hope you have learned alot about power markets and the complexity with bid offering! It is not as easy for a producer as one may think")
        
        Text.append("")
        Text.append("Although the game is over, let's think first at what you said from the beginning: " + self.Motto +", that was your slogan for your company! Hopefully you managed to fulfill that!")
        
        Text.append("")
        Text.append("Before the game is stopped, let's sum up your precious plants:")
        Text.append("")
        
        for plant in self.Company["ES"]:
            Text.append(plant + " - " + self.Company["ES"][plant]["Nickname"])
            
        Text.append("")
        Text.append("Now with that, thanks again for playing!")
        
        self.PrintMenu(Text)
        self.EnterCommand()
        
        #End EndGame
    
    

    #End Class EndGameClass


class Slave(Print,Text,InitationPhase,StrategyPhaseClass,EndGameClass,BiddingPhaseClass):
    
    def PrintMessage(self,Text):
        print(Text,"\n")
        self.MakePause()
        #End PrintMessage
    
    def MakePause(self):
        time.sleep(0.1)
        #End MakePause
        
    def GetInput(self,Text):
        Text = Text + "\n"
        return(input(Text))
        
        #End GetInput
    def __init__(self,PlayerInfo):
        
        #Store player data in this class
        self.server     = PlayerInfo["Server"]
        self.Name       = PlayerInfo["Name"]
        self.Motto      = PlayerInfo["Motto"]
        
        #Call upon the introduction of the game        
        self.IntroMessage()
        
        #Construct company
        self.ConstructCompany()
        
        #Start the initiation phase
        self.InitiationPhase()
        
        #Create some variables for future use
        self.Result = {}
        self.Round = 0
        
        while True:
            
            #Extract phase info from host
            Command = self.RetrieveData()
            
            #Given phase stored locally
            Phase = Command["Stage"]
            
            #Based on the phase given by host, strategyphase/bidding phase is initiated
            if Phase == 0:
                
                #Run strategy phase
                self.StrategyPhase()
            
            #If bidding phase time
            elif Phase  == 1:
                
                self.bidphase = Command["NumBids"]
                
                #Dictionary storing results is created for this round
                self.Result[self.Round] = {}
                
                #Need to sort out the non-active plants
                #self.MoveInactivePlants()
                
                #Bidding phase initiated
                self.BidPhase()
                
                #Round increased by 1
                self.Round = self.Round + 1
                
                #Update the company based on the results (cash, age, etc)
                self.UpdateCompany()

            elif Phase == 2:
                break
            
            else:
                print("This should not occur...")
                self.Disconnect()
                self.Close()
        
        
        
        self.EndGame()

        self.Disconnect()
        self.Close()
        
        #End __init__
    

    def UpdateCompany(self):
        
        
        
        #Update cash to include profits
        self.UpdateCash()
        
        #for plant in self.Company["ES"]:
        #    self.CheckBuildStatus(self.Company["ES"][plant])
        
        
        """
        This function updates the company data:
            - Cash based on results in bidding phase
            - Age of plants are increased by a year
            - Upgrades are analyzed and completed if conditions are met
            - Plants are deleted if age limit has been met
        """
        
        #End UpdateCompany
        
        
    def UpdateCash(self):
        
        self.Company["Cash"] = self.Company["Cash"] + self.TotalProfit
        
        #End UpdateCash

    
    def RetrieveData(self):
        """This function will retrieve a dictionary and give it as output"""
        

        self.ConnectionMessage()
        
        #Retrieve data        
        inc_dict = self.server.recv(1000000)
        
        #Return dictionary decoded and converted from string to dictionary
        return(json.loads(inc_dict.decode()))
        
        #End RetrieveData
        
    def SendData(self, Data):
        """This function will send the dictionary to the host"""
        
        #Convert to string
        Data = json.dumps(Data)
        
        #Send string to host after encoding it
        self.server.send(Data.encode())
        
        #End SendData
        
    def Disconnect(self):
        
        #Close server connection, freeing up the port
        print("Disconnecting from host...")
        self.server.close()
        
        #End Disconnect
    
    def Close(self):
        
        #Exiting program
        print("Closing down program...")
        
        sys.exit()
        #End Close