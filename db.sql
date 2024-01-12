CREATE DATABASE kampus;

USE kampus;

CREATE TABLE dosen (
    NIDN INT PRIMARY KEY,
    PASSWORD VARCHAR(255) NOT NULL,
    Nama_dosen VARCHAR(255) NOT NULL
);

CREATE TABLE mata_kuliah (
    Kode_MK INT PRIMARY KEY,
    Nama_MK VARCHAR(255) NOT NULL
);

CREATE TABLE dosen_mata_kuliah (
    NIDN INT,
    Kode_MK INT,
    PRIMARY KEY (NIDN, Kode_MK),
    FOREIGN KEY (NIDN) REFERENCES dosen(NIDN),
    FOREIGN KEY (Kode_MK) REFERENCES mata_kuliah(Kode_MK)
);


CREATE TABLE jadwal (
    ID_Jadwal INT PRIMARY KEY,
    Kode_MK INT,
    NIDN INT,
    Hari VARCHAR(10) NOT NULL,
    Jam VARCHAR(20) NOT NULL,
    FOREIGN KEY (Kode_MK) REFERENCES mata_kuliah(Kode_MK),
    FOREIGN KEY (NIDN) REFERENCES dosen(NIDN)
);

ALTER TABLE dosen_mata_kuliah
ADD COLUMN Jadwal_ID INT,
ADD FOREIGN KEY (Jadwal_ID) REFERENCES jadwal(ID_Jadwal);


INSERT INTO dosen (NIDN, PASSWORD, Nama_Dosen) VALUES
(12345, 'password1', 'Dosen A'),
(67890, 'password2', 'Dosen B');

INSERT INTO mata_kuliah (Kode_MK, Nama_MK) VALUES
(1, 'Matematika'),
(2, 'Bahasa Indonesia');


DELIMITER //

CREATE TRIGGER tr_insert_dosen_mata_kuliah
AFTER INSERT ON jadwal
FOR EACH ROW
BEGIN
    DECLARE dosen_id INT;
    DECLARE mata_kuliah_id INT;

    SELECT NIDN, Kode_MK INTO dosen_id, mata_kuliah_id
    FROM jadwal
    WHERE ID_Jadwal = NEW.ID_Jadwal;

    INSERT INTO dosen_mata_kuliah (NIDN, Kode_MK, Jadwal_ID)
    VALUES (dosen_id, mata_kuliah_id, NEW.ID_Jadwal);
END;

//

DELIMITER ;

INSERT INTO jadwal (ID_Jadwal, Kode_MK, NIDN, Hari, Jam) VALUES 
(1, 1, 12345, 'Senin', '08:00-10:00'),
(2, 2, 67890, 'Selasa', '10:00-12:00'),
(3, 2, 12345, 'Senin', '11:00-13:00'),
(4, 1, 67890, 'Senin', '14:00-16:00');
