.libPaths("~/R/library")

library(Matrix)
library(lme4)

anova_pvalue <- numeric(500)

for (i in 1:500) {
  data <- read.csv(paste0("/home/knight/jharrell/hfa_per_outcome_csvs/amygdala/timepoint_", i, ".csv"))
  model <- lmer(value ~ condition + (1 | participant/channel), data)
  anova <- anova(model)
  pvalue <- anova["condition", "Pr(>F)"]
  anova_pvalue[i] <- pvalue
  }
  
anova_pvalue_fdr <- p.adjust(anova_pvalue, method = "fdr")

data <- data.frame(
  timepoint = 1:500,     
  pvalue = anova_pvalue, 
  fdr = anova_pvalue_fdr  
)

write.csv(data, "/home/knight/jharrell/hfa_per_outcome_csvs/pvalues/amygdala_pvalues.csv", 
          row.names = FALSE)

