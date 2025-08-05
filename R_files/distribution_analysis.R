# Load required libraries
library(ggplot2)
library(dplyr)
library(readr)
library(janitor)

# Define file paths
music_research_path <- "~/Desktop/Music Research/"
bebop_file <- file.path(music_research_path, "audio_metrics.csv")
control_file <- file.path(music_research_path, "audio_metrics_control.csv")

# Set directory for saving images
output_dir <- file.path(music_research_path, "distribution_images_part_2")

# Create the directory if it doesn't exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Read and clean CSV files
control_df <- read_csv(control_file) %>% clean_names()
bebop_df <- read_csv(bebop_file) %>% clean_names()

# Add dataset labels
control_df$Dataset <- "Control"
bebop_df$Dataset <- "Bebop"

# Find the minimum dataset size
min_size <- min(nrow(control_df), nrow(bebop_df))

# Randomly sample to match dataset sizes
set.seed(42)
control_sample <- sample_n(control_df, min_size)
bebop_sample <- sample_n(bebop_df, min_size)

# Combine datasets
balanced_df <- bind_rows(control_sample, bebop_sample)

# Get the list of all numerical columns
numerical_columns <- colnames(select(balanced_df, where(is.numeric)))

# Define color scheme
control_color <- "#1f77b4"  # Blue
bebop_color <- "#ff7f0e"    # Orange

# Custom theme for better aesthetics
custom_theme <- theme_minimal(base_size = 14) +
  theme(
    legend.position = "top",
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    axis.text = element_text(size = 12),
    legend.text = element_text(size = 12),
    legend.title = element_blank()
  )

# Generate and save plots for each numerical variable
for (col in numerical_columns) {
  
  # **1️⃣ Density Plot (Overlapping with Transparency)**
  p1 <- ggplot(balanced_df, aes(x = .data[[col]], fill = Dataset)) +
    geom_density(alpha = 0.4, color = "black", linewidth = 1) +
    labs(title = paste("Balanced Distribution of", col), x = col, y = "Density") +
    scale_fill_manual(values = c("Control" = control_color, "Bebop" = bebop_color)) +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_overlapping_density.png")), plot = p1, width = 8, height = 5, dpi = 300)
  
  # **2️⃣ Side-by-Side Density Plots (Facet Grid)**
  p2 <- ggplot(balanced_df, aes(x = .data[[col]])) +
    geom_density(fill = control_color, alpha = 0.5, linewidth = 1) +
    facet_wrap(~Dataset, scales = "free") +
    labs(title = paste("Balanced Distribution of", col), x = col, y = "Density") +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_facet_density.png")), plot = p2, width = 8, height = 5, dpi = 300)
  
  # **3️⃣ Line Density Plot (No Fill, Just Outlines)**
  p3 <- ggplot(balanced_df, aes(x = .data[[col]], color = Dataset)) +
    geom_density(size = 1.5) +
    labs(title = paste("Balanced Distribution of", col), x = col, y = "Density") +
    scale_color_manual(values = c("Control" = control_color, "Bebop" = bebop_color)) +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_line_density.png")), plot = p3, width = 8, height = 5, dpi = 300)
}

# Calculate means for tempo (BPM)
mean(bebop_sample$tempo_bpm, na.rm = TRUE)
mean(control_sample$tempo_bpm, na.rm = TRUE)
