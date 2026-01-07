-- Movies Database Schema and Demo Data

-- Create database
CREATE DATABASE IF NOT EXISTS movies_db;
USE movies_db;

-- Create genres table
CREATE TABLE IF NOT EXISTS genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create movies table
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    release_year INT,
    genre_id INT,
    rating DECIMAL(3,1),
    production_budget DECIMAL(15,2),
    domestic_box_office DECIMAL(15,2),
    international_box_office DECIMAL(15,2),
    global_box_office DECIMAL(15,2),
    description TEXT,
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

-- Create actors table
CREATE TABLE IF NOT EXISTS actors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birth_year INT
);

-- Create movie_actors junction table
CREATE TABLE IF NOT EXISTS movie_actors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    actor_id INT NOT NULL,
    role VARCHAR(255),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES actors(id) ON DELETE CASCADE,
    UNIQUE KEY unique_movie_actor (movie_id, actor_id)
);

-- Insert genres
INSERT INTO genres (name) VALUES
('Action'),
('Adventure'),
('Comedy'),
('Crime'),
('Drama'),
('Horror'),
('Science Fiction'),
('Thriller'),
('Fantasy'),
('Romance');

-- Insert actors
INSERT INTO actors (name, birth_year) VALUES
('Tom Hanks', 1956),
('Leonardo DiCaprio', 1974),
('Morgan Freeman', 1937),
('Meryl Streep', 1949),
('Robert De Niro', 1943),
('Brad Pitt', 1963),
('Scarlett Johansson', 1984),
('Johnny Depp', 1963),
('Emma Stone', 1988),
('Christian Bale', 1974),
('Anne Hathaway', 1982),
('Matt Damon', 1970),
('Cate Blanchett', 1969),
('Jake Gyllenhaal', 1980),
('Natalie Portman', 1981),
('Ryan Gosling', 1980),
('Amy Adams', 1974),
('Michael Fassbender', 1977),
('Jessica Chastain', 1977),
('Benedict Cumberbatch', 1976),
('Denzel Washington', 1954),
('Viola Davis', 1965),
('Hugh Jackman', 1968),
('Keanu Reeves', 1964),
('Gal Gadot', 1985),
('Chris Evans', 1981),
('Zoe Saldana', 1978),
('Mahershala Ali', 1974),
('Florence Pugh', 1996),
('Pedro Pascal', 1975),
('John Travolta', 1954);

-- Insert movies
INSERT INTO movies (title, director, release_year, genre_id, rating, description) VALUES
('The Shawshank Redemption', 'Frank Darabont', 1994, 5, 9.3, 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'),
('The Godfather', 'Francis Ford Coppola', 1972, 4, 9.2, 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.'),
('The Dark Knight', 'Christopher Nolan', 2008, 1, 9.0, 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.'),
('Pulp Fiction', 'Quentin Tarantino', 1994, 4, 8.9, 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'),
('Forrest Gump', 'Robert Zemeckis', 1994, 5, 8.8, 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.'),
('Inception', 'Christopher Nolan', 2010, 7, 8.8, 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.'),
('The Matrix', 'Lana Wachowski, Lilly Wachowski', 1999, 7, 8.7, 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.'),
('Goodfellas', 'Martin Scorsese', 1990, 4, 8.7, 'The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.'),
('Interstellar', 'Christopher Nolan', 2014, 7, 8.6, 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.'),
('The Departed', 'Martin Scorsese', 2006, 4, 8.5, 'An undercover cop and a mole in the police force attempt to identify each other while infiltrating an Irish gang in South Boston.'),
('The Prestige', 'Christopher Nolan', 2006, 7, 8.5, 'After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have.'),
('Gladiator', 'Ridley Scott', 2000, 1, 8.5, 'A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.'),
('The Lion King', 'Roger Allers, Rob Minkoff', 1994, 9, 8.5, 'Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.'),
('The Green Mile', 'Frank Darabont', 1999, 5, 8.6, 'The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder and rape, yet who has a mysterious gift.'),
('Fight Club', 'David Fincher', 1999, 8, 8.8, 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.'),
('The Silence of the Lambs', 'Jonathan Demme', 1991, 8, 8.6, 'A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.'),
('Saving Private Ryan', 'Steven Spielberg', 1998, 1, 8.6, 'Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.'),
('The Usual Suspects', 'Bryan Singer', 1995, 4, 8.5, 'A sole survivor tells of the twisty events leading up to a horrific gun battle on a boat, which began when five criminals met at a seemingly random police lineup.'),
('Se7en', 'David Fincher', 1995, 8, 8.6, 'Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.'),
('The Sixth Sense', 'M. Night Shyamalan', 1999, 6, 8.1, 'A boy who communicates with spirits seeks the help of a disheartened child psychologist.'),
('American History X', 'Tony Kaye', 1998, 5, 8.5, 'A former neo-nazi skinhead tries to prevent his younger brother from going down the same wrong path that he did.'),
('The Pianist', 'Roman Polanski', 2002, 5, 8.5, 'A Polish Jewish musician struggles to survive the destruction of the Warsaw ghetto of World War II.'),
('The Lord of the Rings: The Fellowship of the Ring', 'Peter Jackson', 2001, 9, 8.8, 'A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.'),
('City of God', 'Fernando Meirelles, Kátia Lund', 2002, 4, 8.6, 'In the slums of Rio, two kids\' paths diverge as one struggles to become a photographer and the other a kingpin.'),
('Whiplash', 'Damien Chazelle', 2014, 5, 8.5, 'A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student\'s potential.'),
('The Grand Budapest Hotel', 'Wes Anderson', 2014, 3, 8.1, 'A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy in the hotel\'s glorious years under an exceptional concierge.'),
('12 Years a Slave', 'Steve McQueen', 2013, 5, 8.1, 'In the antebellum United States, Solomon Northup, a free Black man, is abducted and sold into slavery, facing unimaginable hardship while striving to reunite with his family.'),
('X-Men: First Class', 'Matthew Vaughn', 2011, 7, 7.7, 'During the 1960s, Charles Xavier and Erik Lehnsherr form the first class of the X-Men while attempting to stop a global nuclear war.'),
('Steve Jobs', 'Danny Boyle', 2015, 5, 7.2, 'Behind the scenes of three iconic product launches we see the turbulence and brilliance that defined the life of Apple co-founder Steve Jobs.'),
('La La Land', 'Damien Chazelle', 2016, 10, 8.0, 'A jazz pianist and an aspiring actress fall in love while pursuing their dreams in Los Angeles.'),
('Arrival', 'Denis Villeneuve', 2016, 7, 7.9, 'A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world.'),
('Her', 'Spike Jonze', 2013, 10, 8.0, 'A lonely writer develops an unlikely relationship with an operating system designed to meet his every need.'),
('Blade Runner 2049', 'Denis Villeneuve', 2017, 7, 8.0, 'Young Blade Runner K uncovers a long-buried secret that leads him to track down former Blade Runner Rick Deckard.'),
('The Avengers', 'Joss Whedon', 2012, 1, 8.0, 'Earth''s mightiest heroes must come together to stop Loki and his alien army from enslaving humanity.'),
('Guardians of the Galaxy', 'James Gunn', 2014, 7, 8.0, 'A group of intergalactic criminals must pull together to stop a fanatical warrior from taking control of the universe.'),
('Knives Out', 'Rian Johnson', 2019, 8, 7.9, 'A detective investigates the death of the patriarch of an eccentric, combative family.'),
('Logan', 'James Mangold', 2017, 1, 8.1, 'In a future where mutants are nearly extinct, an aging Logan must protect a young mutant from dark forces.'),
('Wonder Woman', 'Patty Jenkins', 2017, 1, 7.4, 'Diana, princess of the Amazons, leaves home to fight a war and discovers her full powers and destiny.'),
('John Wick', 'Chad Stahelski', 2014, 1, 7.4, 'An ex-hitman comes out of retirement to track down the gangsters that killed his dog and took everything from him.'),
('Fences', 'Denzel Washington', 2016, 5, 7.2, 'A working-class African-American father tries to raise his family in the 1950s while coming to terms with events of his life.'),
('Moonlight', 'Barry Jenkins', 2016, 5, 7.4, 'A young African-American man grapples with his identity and sexuality while experiencing the everyday struggles of childhood, adolescence, and burgeoning adulthood.'),
('Little Women', 'Greta Gerwig', 2019, 5, 7.8, 'Jo March reflects back and forth on her life, telling the beloved story of the March sisters.'),
('The Equalizer', 'Antoine Fuqua', 2014, 8, 7.2, 'A former Marine and DIA operative turns vigilante to help those who cannot defend themselves.'),
('Prospect', 'Christopher Caldwell, Zeek Earl', 2018, 7, 6.7, 'A teenage girl and her father travel to a remote alien moon looking for riches, but find more dangers than they expected.');

-- Backfill sample box office data (USD)
UPDATE movies SET
    production_budget = 25000000,
    domestic_box_office = 28341469,
    international_box_office = 58500000,
    global_box_office = 86841469
WHERE title = 'The Shawshank Redemption';

UPDATE movies SET
    production_budget = 6000000,
    domestic_box_office = 13496800,
    international_box_office = 21500000,
    global_box_office = 34996800
WHERE title = 'The Godfather';

UPDATE movies SET
    production_budget = 185000000,
    domestic_box_office = 533345358,
    international_box_office = 469700000,
    global_box_office = 1003045358
WHERE title = 'The Dark Knight';

UPDATE movies SET
    production_budget = 63000000,
    domestic_box_office = 108561006,
    international_box_office = 214200000,
    global_box_office = 322761006
WHERE title = 'Inception';

UPDATE movies SET
    production_budget = 170000000,
    domestic_box_office = 292576195,
    international_box_office = 487100000,
    global_box_office = 779676195
WHERE title = 'Interstellar';

UPDATE movies SET
    production_budget = 150000000,
    domestic_box_office = 260998509,
    international_box_office = 370800000,
    global_box_office = 631798509
WHERE title = 'The Matrix';

UPDATE movies SET
    production_budget = 65000000,
    domestic_box_office = 142502728,
    international_box_office = 174200000,
    global_box_office = 316702728
WHERE title = 'La La Land';

UPDATE movies SET
    production_budget = 47000000,
    domestic_box_office = 101000000,
    international_box_office = 125000000,
    global_box_office = 226000000
WHERE title = 'Arrival';

UPDATE movies SET
    production_budget = 220000000,
    domestic_box_office = 623357910,
    international_box_office = 895457070,
    global_box_office = 1518814980
WHERE title = 'The Avengers';

UPDATE movies SET
    production_budget = 149000000,
    domestic_box_office = 412563408,
    international_box_office = 409500000,
    global_box_office = 822063408
WHERE title = 'Wonder Woman';

-- Insert movie_actors relationships
INSERT INTO movie_actors (movie_id, actor_id, role) VALUES
(1, 3, 'Ellis Boyd "Red" Redding'),
(2, 5, 'Vito Corleone'),
(3, 10, 'Bruce Wayne / Batman'),
(4, 31, 'Vincent Vega'),
(5, 1, 'Forrest Gump'),
(6, 2, 'Dom Cobb'),
(7, 10, 'Thomas Anderson / Neo'),
(8, 5, 'James Conway'),
(9, 10, 'Cooper'),
(10, 2, 'Billy Costigan'),
(10, 12, 'Colin Sullivan'),
(11, 10, 'Alfred Borden'),
(12, 1, 'Maximus Decimus Meridius'),
(14, 1, 'Paul Edgecomb'),
(15, 6, 'Tyler Durden'),
(16, 1, 'Clarice Starling'),
(17, 1, 'Captain John H. Miller'),
(18, 6, 'Verbal Kint'),
(19, 6, 'Detective David Mills'),
(20, 1, 'Dr. Malcolm Crowe'),
(21, 6, 'Derek Vinyard'),
(22, 2, 'Władysław Szpilman'),
(23, 10, 'Aragorn'),
(25, 13, 'Terence Fletcher'),
(26, 18, 'Edwin Epps'),
(27, 18, 'Erik Lehnsherr / Magneto'),
(28, 18, 'Steve Jobs'),
(30, 16, 'Sebastian Wilder'),
(30, 9, 'Mia Dolan'),
(31, 17, 'Dr. Louise Banks'),
(32, 7, 'Samantha (voice)'),
(32, 17, 'Amy'),
(33, 16, 'Officer K'),
(34, 26, 'Steve Rogers / Captain America'),
(34, 7, 'Natasha Romanoff / Black Widow'),
(35, 27, 'Gamora'),
(36, 26, 'Ransom Drysdale'),
(37, 23, 'Logan / Wolverine'),
(38, 25, 'Diana Prince / Wonder Woman'),
(39, 24, 'John Wick'),
(40, 21, 'Troy Maxson'),
(40, 22, 'Rose Lee Maxson'),
(41, 28, 'Juan'),
(42, 29, 'Amy March'),
(43, 21, 'Robert McCall'),
(44, 30, 'Ezra');

