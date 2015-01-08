from BSE import Trader, Order
from BSE import Trader_Giveaway, Trader_ZIC, Trader_Shaver, Trader_ZIP, Trader_Sniper

from numpy.random import normal
from random import choice

from numpy import argmax
from time import time
from os.path import isfile
from math import sqrt, log
from collections import deque

class Trader_MAB( Trader ):


  def __init__(self, ttype, tid, balance):
    # Predefine initial parameters
    self.hisLen = 10
    self.norm = float(1000 - 1) # based on max and min price on market
    self.panic = 0.1
    ##############################

    self.clearout = False
    self.lastBB = 0
    self.lastAB = 0

    self.payout = None # payout for current trade
    self.createStats = True
    self.singleStats = True

    self.transactionInProgress = None

    # get order to issue
    self.orderToIssue = None

    # Remember your assets
    self.assets = { 'bought':[], 'sold':[] }
    self.maxAssets = 3
    self.orderQueue = []

    # Remember recent price history
    self.priceHistory = { 'bids':{'best':deque(maxlen=self.hisLen), 'worst':deque(maxlen=self.hisLen)}, 'asks':{'best':deque(maxlen=self.hisLen), 'worst':deque(maxlen=self.hisLen)} }

    self.statsFilename = "MAB_stats.csv"
    self.statsFile = isfile(self.statsFilename) #? if concurrent run first round is lost
    # ############################

    self.ttype = ttype
    self.tid = tid

    self.balance = 0
    self.initialMoney = balance
    self.givenCash = balance

    self.blotter = []
    self.orders = []
    self.willing = 1        #?
    self.able = 1           #?
    self.lastquote = None   #?

    # Initialise all traders predefined for this system: GVWY, ZIC, SHVR, SNPR, ZIP, MAB
    self.keys = [ 'GVWY', 'ZIC', 'SHVR', 'SNPR', 'ZIP' ]
    self.traders = { 'GVWY' : Trader_Giveaway('GVWY', None, 0.0),
      'ZIC' : Trader_ZIC('ZIC', None, 0.0),
      'SHVR' : Trader_Shaver('SHVR', None, 0.0),
      'SNPR' : Trader_Sniper('SNPR', None, 0.0),
      'ZIP' : Trader_ZIP('ZIP', None, 0.0) }

    self.currentTraderID = choice( self.keys )

    ## Get all available traders count
    self.tradersNo = len(self.traders)

    # Initialise 'trade-ness' parameters | algorithm use count & earned values
    # self.mu = dict( zip(self.keys, self.tradersNo * [self.earn]) )
    # self.sigma = dict( zip(self.keys, self.tradersNo * [self.uncertainty]) )
    self.tStats = dict( zip(self.keys, self.tradersNo * [0]) )
    # self.reward = dict( zip(self.keys, self.tradersNo * [[0]]) )
    self.value = dict( zip(self.keys, self.tradersNo * [0.0]) )

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

    # print self.orders[0].price
    if order.otype == 'Bid':
      # Just bought so reduce initial Money

      # check if I have shorted something buy it back
      if len(self.assets['sold']) != 0:
        # Find the worse price of shortage
        minimum = min(self.assets['sold'])
        profit = transactionprice + minimum
        # Delete from short list
        print "Bing"
        self.assets['sold'].remove( minimum )
      else:
        profit = 0
        self.initialMoney -= transactionprice
        #memorise in self.assets to calculate profit later
        self.assets['bought'].append( transactionprice )
      
      
    elif order.otype == 'Ask':
      if len(self.assets['bought']) != 0: # sell something I bought
        # sell what I have - find the maximum that I paid
        maximum = max(self.assets['bought'])
        profit = transactionprice-maximum
        # Record
        self.assets['bought'].remove( maximum )
      else: # short it
        # sell short - record
        print "Bang"
        self.assets['sold'].append( -transactionprice )
        profit = -transactionprice
        # there is nothing to do with initial money
    else:
      sys.exit('FATAL: MAB doesn\'t know .otype %s\n' % order.otype)

    # fill the account and stay with commission
    if self.initialMoney == self.givenCash: # all profit for me
      self.balance += profit
    elif self.initialMoney > self.givenCash: # to much in bank-payout
      over = self.givenCash - self.initialMoney
      self.initialMoney -= over
      profit += over
      self.balance +=  profit
    elif self.initialMoney < self.givenCash:
      under = self.givenCash - self.initialMoney
      self.initialMoney += under
      profit -= under
      self.balance += profit

    if verbose: print('%s profit=%d balance=%d ' % (outstr, profit, self.balance))
    self.del_order(order) # delete the order

    # Remember about sub-traders
    for traderID in self.traders:
        self.traders[traderID].del_order(None) # bookkeep(trade, order, verbose)
    # memorise profit
    self.payout = profit
    self.transactionInProgress = None


  # Get order, calculate trading price, and schedule
  def getorder( self, time, countdown, lob ):

    # Choose sub-algorithm
    def selfChoice(toTry):
      # If any option has not been used so far use it # Identify trader associated with choice
      val = [self.tStats[x] for x in toTry]
      zeroes = val.count(0)

      if zeroes != 0:
        IDs = [key for key in toTry if self.tStats[key] == 0]
        self.currentTraderID = choice(IDs)
      else:
        ucb_values = [0.0] * len(toTry)
        total_counts = sum( self.tStats.values() )
        for i, key in enumerate(toTry):
          bonus = sqrt((2 * log(total_counts)) / float(self.tStats[key] ))
          reward = self.value[key] #sum(self.reward[key])/float(len(self.reward[key]))
          ucb_values[i] = reward + bonus # Give average earn
        self.currentTraderID = toTry[argmax(ucb_values)]


    if countdown < self.panic:
      self.clearout = True

    if len( self.orders ) < 1:
      order = None
    else:
      ## Memorise order - #? LAZY assumes only one order
      self.recentOrder = self.orders[-1]

      # Create a list of sub-traders tried in this round
      notTried = self.keys[:]

      while( len(notTried) > 0 ):
        # Select sub-algorithm
        selfChoice(notTried)

        # Record attempt
        notTried.remove(self.currentTraderID)

        ## Simulate chosen trader and get order from it
        externalOrder = self.traders[self.currentTraderID].getorder( time, countdown, lob )

        # Construct order: substitute tid due to external touch of trader shuffle
        # If None choose other trader and penalise selected for not taking a shoot
        if externalOrder == None:
          order = None
          # Penalise current algorithm for not making the move
          # and choose again via loop
        else:
          ## Issue order
          order = Order(self.tid, externalOrder.otype, externalOrder.price, externalOrder.qty, time)
          break

    self.orders = [order]
    return order


  # Update trader's statistics based on current market situation
  def respond(self, time, lob, trade, verbose):

    # Calculate k-lag's
    def lag( current, series ):
      lags = []
      for i in series:
        lags.append(current-i)
      return lags

    # Decide whether to buy / sell and give appropriate order
    ## Wait 5% of the time to discover trend: I first have to buy
    # analyse *self.assets*

    # Remember about sub-traders #self.traders[self.currentTraderID].respond(time, lob, trade, verbose)
    for traderID in self.traders:
      self.traders[traderID].respond(time, lob, trade, verbose)      

    self.orderToIssue = None

    # update sub-traders estimates: adapt trader to current market structure
    if trade != None and self.payout != None:
      ## Record trader choice or later statistics
      self.tStats[self.currentTraderID] += 1

      n = self.tStats[self.currentTraderID]
      value = self.value[self.currentTraderID]
      payout = self.payout / self.norm *20
      if payout > 1:
        print "Payout misuse: ", payout
      elif payout <= 0:
        payout = 0.00000000001
      new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * payout 
      self.value[self.currentTraderID] = new_value
      self.payout = None

    # Check for current prices on the market to decide
    bbFluc = None
    bbTrend =None
    # bwFluc = None
    # bwTrend =None
    abTrend =None
    abFluc = None
    # awTrend =None
    # awFluc = None
    bb = lob['bids']['best']
    if bb != None:
      bbFluc = lag( bb, list(self.priceHistory['bids']['best']) )
      bbTrend = sum(bbFluc)
    else:
      bb = 0
      bbTrend = 0

    # bw = lob['bids']['worst']
    # if bw != None:
    #   bwFluc = lag( bw, list(self.priceHistory['bids']['worst']) )
    #   bwTrend = sum(bwFluc)
    # else:
    #   bw = 0

    ab = lob['asks']['best']
    if ab != None:
      abFluc = lag( ab, list(self.priceHistory['asks']['best']) )
      abTrend = sum(abFluc)
    else:
      ab = 0
      abTrend = 0

    # aw = lob['asks']['worst']
    # if aw != None:
    #   awFluc = lag( aw, list(self.priceHistory['asks']['worst']) )
    #   awTrend = sum(awFluc)
    # else:
    #   aw = 0


    # Check if clear-out
    if False:#self.clearout:
      # get rid of all you have
      # if there is any bought asset: sell it
      if len(self.assets['bought']) > 0:
        # Find top paid price
        p = max(self.assets['bought'])
        o = Order(self.tid, 'Ask', p, 1, time)
        # self.orderQueue.append(o)
        self.orderToIssue = o
      # if there is any shorted asset: buy it back
      elif len(self.assets['sold']) > 0:
        # Find top paid price
        p = max(self.assets['sold'])
        o = Order(self.tid, 'Bid', p, 1, time)
        # self.orderQueue.append(o)
        self.orderToIssue = o
      # I have nothing: do nothing
      else:
        pass
    # proceed with trading
    else:
      # Check whether maximal number of assets reached
      action = self.transactionInProgress
      if self.transactionInProgress == None:
        action = 'free'
        # bought = bought; sold = shorted -- only one can be > 0
        # if (len(self.assets['bought']) + len(self.orders)) >= 3:
        if len(self.assets['bought']) > 0:
          action = 'sell'
        # elif (len(self.assets['sold']) + len(self.orders)) >= 3:
        elif len(self.assets['sold']) > 0:
          action = 'buy'
        self.transactionInProgress = action

      # print self.lastBB - bbTrend
      # print self.lastAB - abTrend, "\n"
      
      if action == 'sell': # sell
        # if upward trajectory in price act
        if bbTrend>0:
          # if asks peaked make an offer
          p = max(self.assets['bought']) # if not working try min
          if bbTrend - self.lastBB > 0 and p >= lob['bids']['best'] :
            o = Order(self.tid, 'Ask', p, 1, time)
            # self.orderQueue.append(o)
            self.orderToIssue = o
          else: # wait for peak
            pass
        else: # wait
          pass


      elif action == 'buy': # buy


        # if downward trajectory in price act
        if abTrend<0:
          # if asks peaked make an offer
          p = abs( max(self.assets['sold']) ) # if not working try min
          if abTrend - self.lastAB < 0 and p <= lob['asks']['best'] :
            o = Order(self.tid, 'Bid', p, 1, time)
            # self.orderQueue.append(o)
            self.orderToIssue = o
          else: # wait for peak
            pass
        else: # wait
          pass


      elif action == 'free': # do whatever you want
        # based on what trends better buy or sell
        # if buyers want to pay more and more try to sell
        if (bbTrend - self.lastBB) >= (self.lastAB - abTrend) and bbTrend>0 and len(self.assets['bought']) > 0:
          # Sell
          if bbTrend - self.lastBB > 0 :
            o = Order(self.tid, 'Ask', lob['bids']['best'], 1, time)
            # self.orderQueue.append(o)
            self.orderToIssue = o

        # if seller want to sell for less and less try to buy
        elif (bbTrend - self.lastBB) <= (self.lastAB - abTrend) and abTrend>0:
          # Buy
          if abTrend - self.lastAB < 0 :
            o = Order(self.tid, 'Bid', lob['asks']['best'], 1, time)
            # self.orderQueue.append(o)
            self.orderToIssue = o
        else:
          #wait
          pass
      
      else: # error
        sys.exit('MAB: action undefined-%s' % action)


    # Check for order queue and if available engage
    # if len(self.orders) == 0 and len(self.orderQueue) != 0:
    #   self.add_order(self.orderQueue.pop(0))

    # Make history
    # BB & BA
    self.lastBB = bbTrend
    self.lastAB = abTrend
    self.priceHistory['bids']['best'].append(bb)
    # self.priceHistory['bids']['worst'].append(bw)
    self.priceHistory['asks']['best'].append(ab)
    # self.priceHistory['asks']['worst'].append(aw)
    if self.orderToIssue != None:
      self.add_order(self.orderToIssue)

    if len(self.assets['sold']) != 0:
      print len(self.assets['sold'])
