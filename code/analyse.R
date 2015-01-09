# R script for analysis

# Read Data
mydata = read.csv("~/Dropbox/Year_4/Algorithmic and Economic Aspects of the Internet/CW/code/untitled folder/balances_004 copy 2.csv")

# Extract rows
gwy <- mydata[,6]
mab <- mydata[,10]
shvr<- mydata[,14]
zic <- mydata[,18]
zip <- mydata[,22]

# Do avg, median, std
mean.gwy <- mean(gwy )
mean.mab <- mean(mab )
mean.shvr<- mean(shvr)
mean.zic <- mean(zic )
mean.zip <- mean(zip )

median.gwy <- median(gwy )
median.mab <- median(mab )
median.shvr<- median(shvr)
median.zic <- median(zic )
median.zip <- median(zip )

sd.gwy <- sd(gwy )
sd.mab <- sd(mab )
sd.shvr<- sd(shvr)
sd.zic <- sd(zic )
sd.zip <- sd(zip )


# Generate matrix
GWY <- gwy
MAB <- mab
SHVR <- shvr
ZIC <- zic
ZIP <- zip
mx <- cbind( GWY, MAB, SHVR, ZIC, ZIP )


boxplot(mx, main="", xlab="Trader", ylab="Profit")

name.gwy <- rep( c("GWY"), length(GWY))#mydata[,3]
name.mab <- rep( c("MAB"), length(MAB))#mydata[,7]
name.shvr<- rep( c("SHVR"), length(SHVR))#mydata[,11]
name.zic <- rep( c("ZIC"), length(ZIC))#mydata[,15]
name.zip <- rep( c("ZIP"), length(ZIP))#mydata[,19]

names <- c( name.gwy, name.mab, name.shvr, name.zic, name.zip  )
values <- c(GWY, MAB, SHVR, ZIC, ZIP )
# nam.val <- cbind( names, values )

frame <- data.frame(values, names)
names(frame) <- c("Profit","Type")


pairwise.wilcox.test( Profit, Type )

# kruskal.test(Profit ~ Type, data=frame)

# require(PMCMR)
# data(frame)
# attach(frame)
# posthoc.kruskal.nemenyi.test(x=Profit, g=Type, method="Tukey")


# Analyse sub traders
sub = read.csv("~/Dropbox/Year_4/Algorithmic and Economic Aspects of the Internet/CW/code/untitled folder/MAB_stats.csv")
sum(sub[,1])
sum(sub[,2])
sum(sub[,3])
sum(sub[,4])
sum(sub[,5])

mean(rowSums(sub))








