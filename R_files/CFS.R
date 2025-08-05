# Install required packages (if not already installed)
install.packages("tidyverse")
install.packages("tidytext")
install.packages("textdata")  # For sentiment lexicons
install.packages("wordcloud")  # For word cloud visualization

# Load the necessary libraries
library(tidyverse)
library(tidytext)
library(textdata)
library(wordcloud)

la_times_text <- "Thousands of demonstrators rallied in downtown Los Angeles on Sunday and shut down a section of the 101 Freeway to protest President Trump’s crackdown on illegal immigration and his aggressive deportation policies. Draped in Mexican and Salvadoran flags, demonstrators gathered near City Hall shortly before noon, blocking traffic at Spring and Temple streets, amid honking horns and solidarity messages from passing motorists. Protesters blasted a mix of traditional and contemporary Mexican music from a loudspeaker, and some danced in the road in traditional feathered headdresses.

The protests continued into the evening. After a citywide tactical alert was issued around 7 p.m., L.A. police officers were deployed downtown in riot gear, equipped with helmets, batons and less-than-lethal weapons, according to Tony Im, spokesperson for the Los Angeles Police Department.

Near Union Station, officers formed lines to stop the protesters and push them back, he said. As of 10 p.m., there were no reports of arrests or injuries. Police remained at the scene, Im said, as there were “still areas where we are addressing the situation.” Videos posted on social media after 10 p.m. showed police calling for protesters to disperse.

Trump has declared a crisis at the southern border and released a flurry of executive orders aimed at revamping the country’s immigration system and promising to deport millions of people who are in the country illegally. Protesters told The Times that it was those actions that prompted them to rally downtown.

By 1 p.m., the number of protesters ballooned to several thousand, with some carrying signs that said, “MAGA — Mexicans always get across”; “Don’t bite the hand that feeds you,” referring to the state’s agricultural workers; and “I drink my horchata warm because f— I.C.E.,” a reference to the U.S. Immigration and Customs Enforcement agency.

Nailah Esparza, 18, said that it was her first protest and that she learned about it about a week ago from TikTok videos. She held a sign in Spanish that read, “No more I.C.E. raids, no more fear, we want justice and a better world.”

“It was actually something that was very important, so we decided to show support, because of the youth,” said Esparza, who is Mexican American. “We’re very passionate about what we’re here for.”

Another protester, who identified himself only as Rey out of privacy concerns, brought a sign that read, “Trump eat caca! Beware the Nazis.” He said he protested Trump’s immigration policies during his first term as president.

“We thought we were done with his administration,” said Rey, who is Mexican American. “And now we have to do this again.”

The demonstration was largely peaceful, with some enterprising street vendors taking advantage of the moment to sell bacon-wrapped hot dogs, ice cream, churros, beer and even shots of Patron tequila.

But things appeared to ratchet up when the driver of a silver Mustang began doing doughnuts in a usually busy intersection near City Hall. Soon after, a few police cars arrived as dozens of protesters walked onto the nearby 101 Freeway, while hundreds more crowded overpasses, waving flags and holding signs.

But police — whose presence early in the demonstration was minimal — did not converge on the demonstrators, even as throngs made their way onto the freeway. A section of the freeway near the 110 interchange was shut down around noon and remained closed shortly after 4 p.m., officials said.

Im said on Sunday afternoon that the department was “staffed adequately” to handle the protests but declined to elaborate on staffing details.

A short time after the freeway takeover began, the acrid smell of burning tires hung in the air as trucks and motorcycles did noisy burnouts on an overpass, drawing cheers and cameras amid the noisy din of car horns, police sirens and helicopters overhead.

By 8 p.m., protesters were cleared and the 101 Freeway was reopened, according to the California Highway Patrol.

Promising the largest deportation effort in U.S. history, Trump, in his first days in office, declared a national emergency at the southern border, deploying troops there.

His executive orders sharply limit legal pathways for entering the United States, bolster enforcement efforts to seal off the U.S.-Mexico border, and promote aggressive sweeps to round up and deport people who are not authorized to be in the United States. Some of the orders have been challenged in court, and advocates said others could be soon.

There are an estimated 11 million to 15 million undocumented immigrants in the U.S., including more than 2 million in California.

They include people who crossed the border illegally, people who overstayed their visas and people who have requested asylum. It does not include people who entered the country under various temporary humanitarian programs, or who have obtained temporary protected status, which gives people the right to live and work in the U.S. temporarily because of disasters or strife in their home countries."



fox_news_text <- "Hundreds of protesters flooded a busy Los Angeles freeway on Sunday morning, causing major traffic delays in response to President Donald Trump's illegal immigration crackdown.

The protest began on Olvera Street at around 9 a.m. with a large group of participants. Nearly half an hour later, the Los Angeles Police Department (LAPD) announced several street closures due to 'a non-permitted demonstration blocking traffic' and suggested drivers find alternate routes.

The California Highway Patrol also confirmed the protests and encouraged people to avoid downtown Los Angeles while authorities attempted to gain control of the demonstration.

'Please avoid the 101 freeway in DTLA between I-110 and Mission Rd., as we work to remove a protest from the freeway. Accessing state highways or roads to protest is unlawful and extremely dangerous because it puts protesters, motorists and first responders at great risk of injury,' CHP wrote on X.

Many of the protesters could be seen carrying signs, waving Mexican flags and speaking out against Trump’s immigration policies. Officers could also be seen in riot gear and engaged in a standoff with the protesters.

'No human is illegal on stolen land,' one sign read.

Another one read, 'fight ignorance, not immigrants.'

Videos shared on social media show what appeared to be demonstrators spraying graffiti on the freeway walls and vandalizing at least one car that was stopped in the middle of the crowd.

'They shut down freeways and stop traffic in one of the most congested cities in the U.S. to try to convince us not to deport them,' popular conservative account Libs of TikTok wrote on X while sharing video of the incident. 'This isn’t gonna end well. Get ICE on scene ASAP.'

Conservative influencer Benny Johnson also shared video of the protests, agreeing that 'this will not end well for them.'

'FAFO: Mass deportation protesters completely blocked 101 Freeway in downtown Los Angeles. Not only are they illegally in our country, they are now illegally blocking roads. This will not end well for them,' Johnson wrote on X.

Trump has received backlash from several Democrat leaders who have vowed to fight back against his deportation operation.

White House Press Secretary Karoline Leavitt announced Friday that deportation flights have begun, releasing photos of illegal immigrants boarding military aircraft.

'President Trump is sending a strong and clear message to the entire world: if you illegally enter the United States of America, you will face severe consequences,' she previously wrote on X.

Immigration and Customs Enforcement (ICE) has arrested more than 7,400 illegal immigrants nationwide in nine days amid its aggressive crackdown propelled by the new Trump administration. The agency also said it has placed nearly 6,000 ICE detainers.

ICE officers have been seen carrying out raids at homes, work sites and other establishments, while the Trump administration has vowed to send the most violent illegal immigrants to Guantánamo Bay.

Border czar Tom Homan has said the administration is targeting violent illegal aliens at the moment. Homeland Security Secretary Kristi Noem, who oversees ICE, also said federal immigration authorities are arresting the 'worst of the worst' in raids."

# Create a tibble with the articles
articles <- tibble(
  source = c("LA Times", "Fox News"),
  text = c(la_times_text, fox_news_text)  # Adding the full text variables
)

# Step 2: Tokenize the text into individual words
tidy_articles <- articles %>%
  unnest_tokens(word, text)  # Breaks down text into words

# Step 3: Remove stop words (common words that don’t carry sentiment)
tidy_articles <- tidy_articles %>%
  anti_join(stop_words, by = "word")

exclude_words <- c("trump", "biden", "obama")  # Add any other proper nouns as needed

# Exclude these words during sentiment analysis
tidy_articles <- tidy_articles %>%
  filter(!word %in% exclude_words)

# Tokenize the text and count word frequency
word_counts <- articles %>%
  unnest_tokens(word, text) %>%
  anti_join(stop_words, by = "word") |> 
  count(source, word, sort = TRUE)

# View the top words for each source
print(word_counts) |> 
  print(n = 30)

# Filter for "illegal" and "illegally" in both articles
word_difference <-word_counts %>%
  filter(word %in% c("illegal", "illegally"))

# Print the results
print(word_difference)

# Plot the occurrences of "illegal" and "illegally" in each article
ggplot(word_difference, aes(x = word, y = n, fill = source)) +
  geom_col(position = "dodge") +  # Side-by-side bars
  labs(title = "Usage of 'Illegal' and 'Illegally' in News Articles",
       x = "Word",
       y = "Count") +
  theme_minimal()

# Step 4: Perform Sentiment Analysis using Bing Lexicon
bing_sentiments <- tidy_articles %>%
  inner_join(get_sentiments("bing"), by = "word") %>%
  count(source, sentiment) %>%
  pivot_wider(names_from = sentiment, values_from = n, values_fill = 0) %>%
  mutate(sentiment_score = positive - negative)  # Compute sentiment score

# Print sentiment scores
print(bing_sentiments)

# Step 5: Visualize Sentiment Scores with a Bar Plot
bing_sentiments %>%
  pivot_longer(cols = c(positive, negative), names_to = "sentiment", values_to = "count") %>%
  ggplot(aes(x = source, y = count, fill = sentiment)) +
  geom_col(position = "dodge") +
  labs(title = "Sentiment Analysis of LA Times vs. Fox News Articles",
       y = "Word Count",
       x = "News Source") +
  theme_minimal()

# Step 6: Identify the Most Common Sentiment Words
top_sentiment_words <- tidy_articles %>%
  inner_join(get_sentiments("bing"), by = "word") %>%
  count(word, sentiment, sort = TRUE)

# Plot top sentiment words
top_sentiment_words %>%
  group_by(sentiment) %>%
  slice_max(n, n = 10) %>%
  ggplot(aes(reorder(word, n), n, fill = sentiment)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~sentiment, scales = "free_y") +
  coord_flip() +
  labs(title = "Most Common Sentiment Words in Both Articles",
       x = "Word",
       y = "Frequency") +
  theme_minimal()

# Step 7 (Optional): Word Cloud of Sentiment Words
tidy_articles %>%
  inner_join(get_sentiments("bing"), by = "word") %>%
  count(word, sentiment, sort = TRUE) %>%
  with(wordcloud(word, n, max.words = 100, colors = c("red", "blue")))

positive_words_by_source <- tidy_articles %>%
  inner_join(get_sentiments("bing") %>% filter(sentiment == "positive"), by = "word") %>%
  count(source, word, sort = TRUE)

negative_words_by_source <- tidy_articles %>%
  inner_join(get_sentiments("bing") %>% filter(sentiment == "negative"), by = "word") %>%
  count(source, word, sort = TRUE)

# View the top 20 positive words for each article
positive_words_by_source %>%
  group_by(source) %>%
  slice_max(n, n = 20) %>%
  print(n = 40)  # Show top 20 for each source

negative_words_by_source <- negative_words_by_source |> 
  slice_head(n = 10)

ggplot(positive_words_by_source, aes(x = reorder(word, n), y = n, fill = source)) +
  geom_col(show.legend = TRUE, position = "dodge") +
  coord_flip() +
  labs(title = "Most Common Positive Words in Each Article",
       x = "Positive Words",
       y = "Frequency") +
  theme_minimal()

ggplot(negative_words_by_source, aes(x = reorder(word, n), y = n, fill = source)) +
  geom_col(show.legend = TRUE, position = "dodge") +
  coord_flip() +
  labs(title = "Most Common Negative Words in Each Article",
       x = "Positive Words",
       y = "Frequency") +
  theme_minimal()



