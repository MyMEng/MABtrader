from BSE import Trader, Order
from BSE import Trader_Giveaway, Trader_ZIC, Trader_Shaver, Trader_ZIP, Trader_Sniper

from numpy.random import normal
from random import choice

from numpy import argmax
from time import time
from os.path import isfile
from math import sqrt, log

class Trader_MAB( Trader ):


  def __init__(self, ttype, tid, balance):
    # Predefine initial parameters
    self.earn = 0
    self.uncertainty = 0.1
    self.createStats = True
    self.singleStats = True
    self.statsFilename = "MAB_stats.csv"
    self.statsFile = isfile(self.statsFilename) #? if concurrent run first round is lost
    # ############################

    self.ttype = ttype
    self.tid = tid
    self.balance = balance
    self.blotter = []
    self.orders = []
    self.willing = 1        #?
    self.able = 1           #?
    self.lastquote = None   #?

    # Initialise all traders predefined for this system: GVWY, ZIC, SHVR, SNPR, ZIP, MAB
    self.keys = [ 'GVWY', 'ZIC', 'SHVR', 'SNPR', 'ZIP' ]
    self.traders = { 'GVWY' : Trader_Giveaway('GVWY', None, self.balance),
      'ZIC' : Trader_ZIC('ZIC', None, self.balance),
      'SHVR' : Trader_Shaver('SHVR', None, self.balance),
      'SNPR' : Trader_Sniper('SNPR', None, self.balance),
      'ZIP' : Trader_ZIP('ZIP', None, self.balance) }

    self.currentTraderID = choice( self.keys )

    ## Get all available traders count
    self.tradersNo = len(self.traders)

    # Initialise 'trade-ness' parameters | algorithm use count & earned values
    self.mu = dict( zip(self.keys, self.tradersNo * [self.earn]) )
    self.sigma = dict( zip(self.keys, self.tradersNo * [self.uncertainty]) )
    self.tStats = dict( zip(self.keys, self.tradersNo * [0]) )
    self.reward = dict( zip(self.keys, self.tradersNo * [[]]) )

    # Remember recent order
    self.recentOrder = None

    # Traders statistics
    if self.createStats:
      if self.singleStats:
          if self.statsFile:
            self.tStatsFile = open( self.statsFilename, 'a' )
          else:
            self.tStatsFile = open( self.statsFilename, 'w' )
      else:
        self.tStatsFile = open( ('MAB_stats_%s_%s.csv' % (str(time()).replace('.', '-'), tid)), 'w' )


  # MAnage class destruction
  def __del__(self):

    # Traders statistics
    if self.createStats:
      if self.singleStats:
        if self.statsFile:
          self.tStatsFile.write( "%s\n" % ", ".join(str(x) for x in self.tStats.values()) )
        else:
          self.tStatsFile.write( "%s\n" % ", ".join( self.keys ) )
          self.tStatsFile.write( "%s\n" % ", ".join(str(x) for x in self.tStats.values()) )
      else:
        self.tStatsFile.write( "%s\n" % ", ".join( self.keys ) )
        self.tStatsFile.write( "%s\n" % ", ".join(str(x) for x in self.tStats.values()) )
      self.tStatsFile.flush()
      self.tStatsFile.close()


  def add_order(self, order):
    # in this version, trader has at most one order,
    # if allow more than one, this needs to be self.orders.append(order)
    self.orders=[order]

    # Remember about sub-traders
    for traderID in self.traders:
        self.traders[traderID].add_order(order)


  def bookkeep(self, trade, order, verbose):
    outstr='%s (%s) bookkeeping: orders=' % (self.tid, self.ttype)
    for order in self.orders: outstr = outstr + str(order)

    self.blotter.append(trade) # add trade record to trader's blotter
    # NB What follows is **LAZY** -- assumes all orders are quantity=1
    transactionprice = trade['price']
    if self.orders[0].otype == 'Bid':
      profit = self.orders[0].price-transactionprice
    else:
      profit = transactionprice-self.orders[0].price
    self.balance += profit
    if verbose: print('%s profit=%d balance=%d ' % (outstr, profit, self.balance))
    self.del_order(order) # delete the order

    # Remember about sub-traders
    for traderID in self.traders:
        self.traders[traderID].bookkeep(trade, order, verbose)
    # Append reward to wining sub-trader
    self.reward[self.currentTraderID].append(profit)


  # Get order, calculate trading price, and schedule
  def getorder( self, time, countdown, lob ):


    

    if len( self.orders ) < 1:
      order = None
    else:
      ## Memorise order - #? LAZY assumes only one order
      self.recentOrder = self.orders[-1]




#      ## Get samples
#      action = normal(self.mu.values(), self.sigma.values())
#      ## Choose algorithm
#      choice = argmax(action)
#      ## Check for double occurrences
#      if action.tolist().count(action[choice]) != 1 :
#        indices = [i for i, x in enumerate(action) if x == action[choice]]
#        choice = choice(indices)
#
#      ## Identify trader associated with choice
#      self.currentTraderID = self.keys[choice]


      # Create a list of sub-traders tried in this round
      notTried = self.keys[:]
      # If any option has not been used so far use it # Identify trader associated with choice
      zeroes = self.tStats.values().count(0)
      if zeroes != 0:
        indices = [key for key in self.tStats.keys() if self.tStats[key] == 0]
        self.currentTraderID = choice(indices)
      else:
        ucb_values = [0.0] * self.tradersNo
        total_counts = sum( self.tStats.values() )
        for key in self.tStats.keys():
          bonus = sqrt((2 * log(total_counts)) / float(self.tStats[key] ))
          ucb_values[arm] = self.values[arm] + bonus
        self.currentTraderID = ind_max(ucb_values)

      # Record attempt
      notTried.remove(self.currentTraderID)
      



      ## Record trader choice or later statistics
      if self.createStats:
        self.tStats[self.currentTraderID] += 1

      ## Simulate chosen trader and get order from it
      externalOrder = self.traders[self.currentTraderID].getorder( time, countdown, lob )

      # Construct order: substitute tid due to external touch of trader shuffle
      # If None choose other trader and penalise selected for not taking a shoot
      if externalOrder == None:
        # order = None

      else:
        order = Order(self.tid, externalOrder.otype, externalOrder.price, externalOrder.qty, time)

    return order


  # Update trader's statistics based on current market situation
  def respond(self, time, lob, trade, verbose):

    # Remember about sub-traders #self.traders[self.currentTraderID].respond(time, lob, trade, verbose)
    for traderID in self.traders:
      self.traders[traderID].respond(time, lob, trade, verbose)

    # Ensure that each of the algorithm 

    # Check if currently used algorithm has made a trade and if so update its mean and variance



    # Adapt trader to current market structure
    ## Update posterior based on prior - decide on reward and uncertainty

    ## One component can be simulation of trader: compare trade made with other possibilities
    ##  and check whether could be better
    # self.recentOrder
    # (GVWYo,ZICo,SHVRo,SNPRo,ZIPo) = simulateTrader((time, countdown, lob), traderID)

    ## The other can be ...
    # remember the best LOB data ready for next response
    # could buy for less? raise margin (i.e. cut the price)
    # no deal: aim for target price lower than best ask

    # best bid has improved # NB doesn't check if the improvement was by self

    # trade happened and best ask price has got worse, or stayed same but quantity reduced -- assume previous best ask was lifted

    # if trade != None:
    #   print "Price of just made trade: ", trade['price']
    #   print lob['bids']['best'], " vs. ", lob['bids']['worst']
    #   print lob['asks']['best'], " vs. ", lob['asks']['worst']
    #   print lob['bids']['lob'] # list of orders [price, quantity]
    #   print lob['asks']['lob'] # list of orders [price, quantity]

    # price = self.orders[0].price
    # orderType = self.orders[0].otype
