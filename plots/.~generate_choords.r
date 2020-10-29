require(circlize)

setwd('~/Documentos/multimodal-cognition/')

labels<- c('Visual1', 'Visual2', 'Somatomotor', 
            'Cingulo-Opercular', 'Language', 'Default',
            'Frontoparietal', 'Auditory','Posterior \n Multimodal',
            'Dorsal-attention', 'Ventral \n Multimodal', 'Orbito-Affective')

colours<-c('#0000ffff','#6400ffff','#00ffffff',
           '#990099ff', '#009a9aff',  '#ff0000ff',
           '#ffff00ff',  '#f93dfbff',  '#b15928ff',
           '#00ff00ff',  '#ff9c00ff',  '#417c00ff')

for(case in c("CogTotalComp_Unadj", "CogFluidComp_Unadj", "CogCrystalComp_Unadj")){
  dest.folder<-paste("plots/neurophenotypes", case, sep="/")
  pos_mat<-exp(as.matrix(read.csv(paste(dest.folder, "mean_rsn_pos.txt", sep="/"), 
                                  sep = " ", header = F))*30000)
  
  rownames(pos_mat) <-labels
  colnames(pos_mat) <- rownames(pos_mat)
  
  png(paste(dest.folder, "res_pos_choord.png", sep="/"),  
      width = 5, height =5, units = 'in', res = 300)
  chordDiagram(pos_mat, symmetric=T, grid.col = colours,# column.col = "black", row.col = "black",
               scale=F, keep.diagonal = T, 
               transparency = 0.5, 
               self.link = 2, link.sort = TRUE, link.decreasing = F,
               annotationTrack = c("grid"))
  
  for(si in get.all.sector.index()) {
    xlim = get.cell.meta.data("xlim", sector.index = si, track.index = 1)
    ylim = get.cell.meta.data("ylim", sector.index = si, track.index = 1) + 1.5
    circos.text(mean(xlim), mean(ylim), si, sector.index = si, track.index = 1, 
                #facing = "bending.inside", 
                niceFacing = TRUE, col = "black",cex=0.5, font=2)
  }
  dev.off()
  
  neg_mat<-exp(as.matrix(read.csv(paste(dest.folder, "mean_rsn_neg.txt", sep="/"), 
                                  sep = " ", header = F))*30000)
  
  rownames(neg_mat) <-labels
  colnames(neg_mat) <- rownames(neg_mat)
  
  png(paste(dest.folder, "res_neg_choord.png", sep="/"),  
      width = 5, height =5, units = 'in', res = 300)
  chordDiagram(neg_mat, symmetric=T, grid.col = colours,# column.col = "black", row.col = "black",
               scale=F, keep.diagonal = T, 
               transparency = 0.5, 
               self.link = 2, link.sort = TRUE, link.decreasing = F,
               annotationTrack = c("grid"))
  
  for(si in get.all.sector.index()) {
    xlim = get.cell.meta.data("xlim", sector.index = si, track.index = 1)
    ylim = get.cell.meta.data("ylim", sector.index = si, track.index = 1) + 1.5
    circos.text(mean(xlim), mean(ylim), si, sector.index = si, track.index = 1, 
                #facing = "bending.inside", 
                niceFacing = TRUE, col = "black",cex=0.5, font=2)
  }
  dev.off()
  
  
}

# 
# foo<-read.csv('Documentos/multimodal-cognition/notebooks/foo.txt', sep = " ", header = F)
# 
# foo.mat<-exp(as.matrix(foo)*30000)
# rownames(foo.mat) <- c('Visual1', 'Visual2', 'Somatomotor', 
#                        'Cingulo-Opercular', 'Language', 'Default',
#                        'Frontoparietal', 'Auditory','Posterior \n Multimodal',
#                        'Dorsal-attention', 'Ventral \n Multimodal', 'Orbito-Affective')
# colnames(foo.mat) <- rownames(foo.mat)
# 
# colours<-c('#0000ffff','#6400ffff','#00ffffff',
#   '#990099ff', '#009a9aff',  '#ff0000ff',
#   '#ffff00ff',  '#f93dfbff',  '#b15928ff',
#   '#00ff00ff',  '#ff9c00ff',  '#417c00ff')
# 
# png("~/rsn_chord_example.png",  width = 5, height =5, units = 'in', res = 300)
# chordDiagram(foo.mat, symmetric=T, grid.col = colours,# column.col = "black", row.col = "black",
#              scale=F, keep.diagonal = T, 
#              transparency = 0.5, 
#              self.link = 2, link.sort = TRUE, link.decreasing = F,
#              annotationTrack = c("grid"))
# 
# for(si in get.all.sector.index()) {
#   xlim = get.cell.meta.data("xlim", sector.index = si, track.index = 1)
#   ylim = get.cell.meta.data("ylim", sector.index = si, track.index = 1) + 1.5
#   circos.text(mean(xlim), mean(ylim), si, sector.index = si, track.index = 1, 
#               #facing = "bending.inside", 
#               niceFacing = TRUE, col = "black",cex=0.5, font=2)
# }
# dev.off()
# 
