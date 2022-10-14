#RPi Rmd web generator

 

#install.packages("htmltools")
# install.packages("remotes")
# remotes::install_github("rlesur/klippy")
#library(klippy)

web_repo <- 'https://github.com/JAlcocerT'
web_hosted <- 'https://jalcocert.github.io'

#Get the current wd as the directory of this file
wd<-dirname(rstudioapi::getActiveDocumentContext()$path)
setwd(wd)
#knitt the file on its current folder to test its view
rmarkdown::render('RPi_index.Rmd',
                  output_file = paste('index', 
                                      '.html', sep=''))


#Get the destination to the previous folder
#RPi = substring(wd,1, nchar(wd)-8)

#Copy the newest html file
#file.copy(from = gsub(" ", "", paste(wd,"/index.html")),RPi, overwrite = T)