import psycopg2
from contextlib import closing
try:
    with closing(psycopg2.connect(
            dbname='project',
            user='postgres',
            password='1234567',
            host='localhost',
            port='5432')) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                user_id SERIAL PRIMARY KEY,
                user_mail TEXT NOT NULL,
                user_password TEXT NOT NULL
            );
            
             ALTER TABLE Customers
             ADD COLUMN user_name TEXT DEFAULT 'User';
             
             ALTER TABLE Customers
             ADD CONSTRAINT chk_email CHECK (user_mail ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
            
             CREATE TABLE IF NOT EXISTS Organizers (
                organizer_id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
            
            ALTER TABLE Organizers
            ADD COLUMN user_id INT DEFAULT NULL;
            
            ALTER TABLE Organizers
            ADD CONSTRAINT fk_user_id
            FOREIGN KEY (user_id) REFERENCES Customers(user_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE;

            CREATE TABLE IF NOT EXISTS Categories (
                category_id SERIAL PRIMARY KEY,
                category VARCHAR(100)
            );

            CREATE TABLE IF NOT EXISTS Events (
                event_id SERIAL PRIMARY KEY,
                event_name VARCHAR(250) NOT NULL,
                event_date DATE NOT NULL,
                description TEXT,
                category_id INT NOT NULL REFERENCES Categories(category_id),
                organizer_id INT NOT NULL REFERENCES Organizers(organizer_id),
                city VARCHAR(100) NOT NULL,
                time VARCHAR(50) NOT NULL,
                address VARCHAR(100) NOT NULL,
                photo_path TEXT NOT NULL,
                poster TEXT
            );
            
            ALTER TABLE Events
            ADD COLUMN people_amount INT;
            
            CREATE TABLE IF NOT EXISTS Tickets (
                ticket_id SERIAL PRIMARY KEY,
                event_id INT NOT NULL REFERENCES Events(event_id),
                user_id INT REFERENCES Customers(user_id),
                price INT NOT NULL
            );
            
            ALTER TABLE Tickets
            ADD CONSTRAINT chk_price CHECK (price >= 0);
                        
            ALTER TABLE Events
            ADD CONSTRAINT unique_event_id UNIQUE (event_id);
            
            ALTER TABLE Tickets
            ADD CONSTRAINT unique_ticket_id UNIQUE (ticket_id);
            
            CREATE INDEX find_category_name ON Categories (LOWER(category));
            
            CREATE INDEX find_organizer_name ON Organizers (LOWER(name));
            
            INSERT INTO Categories(category)
            VALUES ('ЧТО ГДЕ КОГДА'),
                   ('Music event'),
                   ('AITUSA event'),
                   ('Party'),
                   ('Competition');
            
            INSERT INTO Organizers(name)
            VALUES ('Mind Games'),
                   ('Music Club'),
                   ('AITUSA'),
                   ('Aitu Live');
            
            
            INSERT INTO Events(event_name, event_date, description, category_id, organizer_id, city, time, address, photo_path, people_amount)
            VALUES  ('Acoustic night', '19-04-2024', 'AITU Music Club invites you to a unique celebration of love and romance! Every year, on April 15th, Kazakhstan celebrates the magnificent holiday - Lovers` Day, inspired by the wonderful Kazakh legend of love «Kozy-Korpesh - Bayan-Sulu»', 2, 2, 'Astana', '18:00', 'Open Space', '1AN.png',200),
                    ('Miss & Mister AITU', '03-05-2024', 'Already on May 3, we will find out who will receive the title of Miss&Mister AITU at an exciting gala concert, where you are expected: Raffle of the merch and unique prizes from sponsors! (For more information, follow our stories)', 5, 3, 'Astana', '16:00', 'Assembly Hall','2MAMA.png',150),
                    ('Финал осенней серии', '19-10-2024', 'After intense intellectual battles, the teams came to a decisive meeting, where every correct answer can be decisive!', 1, 1, 'Astana', '16:00', 'AITU - C1.1.334L','3WWW.png',24),
                    ('AITU Commencement Party', '11-08-2024', 'We are thrilled to invite you to AITU Commencement Party! It`s time to officially join our family and meet new friendse.', 4, 4, 'Astana', '16:00', 'West Hall','4ACP.png',1000),
                    ('Club fair', '18-09-2024', 'AITU has a huge number of clubs. We know that freshmen can`t wait to learn more about each one and already start taking part in student life', 3, 3, 'Astana', '14:00', 'Assembly Hall','5CF.png'),
                    ('Отчетный концерт "Eurasia Band"', '22-11-2024', 'We invite Friends from AITU to attend the Eurasia Band reporting concert. Unforgettable impressions and a warm welcome await you!', 2,2, 'Astana', '17:00', 'КЦДС Атакент','6CEB.png',500),
                    ('Студенческий киновечер', '14-10-2024', 'We are going to watch the movie "Harry Potter and the Goblet of Fire". Don`t miss the chance to immerse yourself in the world of magic and spend time with friends! Come and get a charge of positive emotions!', 4,4, 'Astana', '18:00', 'Assembly Hall','7HPM.png',300),
                    ('Music Spooktacular', '31-10-2024', 'Through the fog of an October night, when the world of the living and the dead almost touch, we invite you to the “Music Spooktacular”', 2,2, 'Astana', '17:00', 'Assembly Hall','8MS.png',300),
                    ('IT FEST 2024','06-12-2024','Conquer the world of technology at ITFest 2024! You are ambitious, striving for new knowledge and want to bring your ideas to life, and ITFest is exactly the place where you can start your path to success!',4,3,'Almaty','9:00','КЦДС Атамекен','ITF9.png',5000);
                    
            
            INSERT INTO Tickets(event_id,price)
            VALUES(1, 1000),
                  (2, 500),
                  (3, 200),
                  (4, 6000),
                  (5, 200),
                  (6, 1000),
                  (7, 1000),
                  (8, 1500),
                  (9,600);
                    
            
            CREATE VIEW event_info
                AS
                SELECT
                event_name, 
                event_date, 
                description, 
                category, 
                name AS organizer_name, 
                time,
                address, 
                photo_path, 
                price,
                timer(event_id) AS timer,
                event_id,
                city,
                ticket_id,
                people_amount
                FROM Events
                LEFT JOIN Categories USING (category_id)
                LEFT JOIN Organizers USING (organizer_id)
                LEFT JOIN Tickets USING (event_id);
            
                
                CREATE OR REPLACE FUNCTION timer(event INT) 
                RETURNS TEXT AS $$
                DECLARE
                    base_date TIMESTAMP := CURRENT_TIMESTAMP;
                    events_date TIMESTAMP;
                    time_diff INTERVAL;
                BEGIN
                    SELECT event_date 
                    INTO events_date
                    FROM Events
                    WHERE event_id = event;
                    IF events_date IS NULL THEN
                        RAISE EXCEPTION 'No event_date found in Events table';
                    END IF;
                    time_diff := events_date - base_date;
                    RETURN 
                        CONCAT(
                            EXTRACT(DAY FROM time_diff), ' дней ',
                            LPAD(EXTRACT(HOUR FROM time_diff)::TEXT, 2, '0'), ':',
                            LPAD(EXTRACT(MINUTE FROM time_diff)::TEXT, 2, '0'), ':',
                            LPAD(EXTRACT(SECOND FROM time_diff)::TEXT, 2, '0')
                        );
                END;
                $$ LANGUAGE plpgsql;
                
                CREATE OR REPLACE FUNCTION decrease_people_amount()
                RETURNS TRIGGER AS $$
                BEGIN
                    UPDATE Events
                    SET people_amount = people_amount - 1
                    WHERE event_id = NEW.event_id;
                    IF (SELECT people_amount FROM Events WHERE event_id = NEW.event_id) < 0 THEN
                        RAISE EXCEPTION 'No more seats available for event %', NEW.event_id;
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                CREATE TRIGGER decrease_seats_trigger
                AFTER INSERT OR UPDATE ON Tickets
                FOR EACH ROW
                EXECUTE FUNCTION decrease_people_amount();
            """)
            print("ok")
except psycopg2.Error as e:
    print(f"{e}")
