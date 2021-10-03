#knitt the file on its current folder to test its view
rmarkdown::render('Index.Rmd',
                  output_file = paste('index', 
                                      '.html', sep=''))

#Get the current wd as the directory of this file
wd<-dirname(rstudioapi::getActiveDocumentContext()$path)
#Set the destination to the previous folder
Financial_analysis_R = substring(wd,1, nchar(wd)-8)

#Copy the newest html file
file.copy(from = gsub(" ", "", paste(wd,"/index.html")),Financial_analysis_R, overwrite = T)