-- MySQL dump 10.14  Distrib 5.5.68-MariaDB, for Linux (x86_64)
--
-- Host: golem24-rds.c3iwaimcc2ui.eu-west-1.rds.amazonaws.com    Database: golem24prod
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `characters`
--
CREATE DATABASE `data`;

USE `data`;

DROP TABLE IF EXISTS `characters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `characters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` char(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `characters`
--

LOCK TABLES `characters` WRITE;
/*!40000 ALTER TABLE `characters` DISABLE KEYS */;
INSERT INTO `characters` VALUES (1,'Katedra'),(2,'Rozmarek'),(3,'Muzeum'),(4,'Ratusz'),(5,'Klasztor Franciszkanów'),(6,'Starostwo Powiatowe'),(7,'Rektorat Uniwersytetu Kaliskiego'),(8,'Park Miejski');
/*!40000 ALTER TABLE `characters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `districts`
--

DROP TABLE IF EXISTS `districts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `districts` (
  `id` int NOT NULL,
  `log_type` varchar(45) DEFAULT NULL,
  `fraction` int DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `districts`
--

LOCK TABLES `districts` WRITE;
/*!40000 ALTER TABLE `districts` DISABLE KEYS */;
INSERT INTO `districts` VALUES (1,'privilege',2),(2,'privilege',3),(3,'privilege',0),(4,'privilege',0),(5,'privilege',0),(6,'privilege',4),(7,'privilege',1),(8,'privilege',0),(1,'occupation',0),(2,'occupation',0),(3,'occupation',0),(4,'occupation',0),(5,'occupation',0),(6,'occupation',0),(7,'occupation',0),(8,'occupation',0);
/*!40000 ALTER TABLE `districts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `final_results_24`
--

DROP TABLE IF EXISTS `final_results_24`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `final_results_24` (
  `patrol_id` int DEFAULT NULL,
  `patrol_name` text,
  `path` text,
  `points` int DEFAULT NULL,
  `houses` text,
  `bonus` text,
  `hint` text,
  `post_cards` text,
  `time` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `final_results_24`
--

LOCK TABLES `final_results_24` WRITE;
/*!40000 ALTER TABLE `final_results_24` DISABLE KEYS */;
INSERT INTO `final_results_24` VALUES (1,'Gambit Kaliski','easy',206,'5','','','',''),(2,'Coozay Familly','easy',203,'5','','','',''),(3,'Szybkie Kury','easy',195,'5','','','',''),(4,'Los Federales','easy',193,'5','','','',''),(5,'Zuzia i mama','easy',191,'5','','','',''),(6,'Do ustalenia na miejscu','easy',191,'5','','','',''),(7,'Kapibary','easy',190,'5','','','',''),(8,'Royal Rangers 54 Odkrywcy 3','easy',189,'5','','','',''),(9,'Mandragora','easy',182,'4','','','',''),(10,'NiezwyciężONE','easy',170,'4','','','',''),(11,'Minionki','easy',168,'4','','','',''),(12,'Wesoła czwóreczka.','easy',162,'4','','','',''),(13,'Royal Rangers 54 Odkrywcy 1','easy',158,'4','','','',''),(14,'Artystki i Nikodem','easy',154,'4','','','',''),(15,'33 KGZ Odważne Wilczki 2','easy',132,'3','','','',''),(16,'33 KGZ Odważne Wilczki 1','easy',125,'3','','','',''),(17,'Szyszunie z Wolicy','easy',124,'3','','','',''),(18,'Poszukiwacze przygód','easy',124,'3','','','',''),(19,'Kaliszanie','easy',106,'2','','','',''),(20,'Szafir','easy',97,'2','','','',''),(21,'Royal Rangers Zwiadowcy 1','easy',94,'2','','','',''),(22,'Royal Rangers Zwiadowcy 2','easy',94,'2','','','',''),(23,'Figlak family','easy',92,'2','','','',''),(24,'Żwawe żbiki','easy',88,'2','','','',''),(25,'3 Gruszki','easy',79,'1','','','',''),(26,'Royal Rangers Zwiadowczynie 2','easy',32,'0','','','',''),(27,'Anastazja','easy',2,'0','','','',''),(28,'Wiewiórki','easy',0,'0','','','',''),(29,'dźenicioł','hard',213,'5','','','',''),(30,'Spalone Podpłomyki z 36 Kaliskiej Drużyny Harcerskiej Orły','hard',203,'5','','','',''),(31,'MacOdkrywcy','hard',201,'5','','','',''),(32,'Pędzące Żółwie','hard',201,'5','','','',''),(33,'EgoTop','hard',190,'4','','','',''),(34,'3DH ZZ','hard',172,'4','','','',''),(35,'Sami z Siebie z 36 Kaliskiej Drużyny Harcerskiej Orły','hard',171,'4','','','',''),(36,'Próchniaki','hard',159,'3','','','',''),(37,'Odważne Wilczki z 36 Kaliskiej Drużyny Harcerskiej Orły','hard',157,'3','','','',''),(38,'Wędrownicy 11 PDW','hard',134,'3','','','',''),(39,'Szybkie żółwie','hard',102,'2','','','',''),(40,'Jastrzębie','hard',102,'2','','','',''),(41,'ElAnia','hard',82,'2','','','',''),(42,'Drużyna Pierścienia','hard',78,'1','','','',''),(43,'Turbo pandy','hard',67,'1','','','',''),(44,'Bobry','hard',48,'0','','','',''),(45,'Daniel Igorewicz z rodziną','hard',42,'0','','','',''),(46,'Tuptusie','hard',34,'0','','','','');
/*!40000 ALTER TABLE `final_results_24` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hints`
--

DROP TABLE IF EXISTS `hints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hints` (
  `id` int NOT NULL,
  `url` varchar(255) DEFAULT NULL,
  `insignum` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `patrol_id` int DEFAULT NULL,
  `fraction` int DEFAULT NULL,
  `point_type` text,
  `point_id` varchar(12) DEFAULT NULL,
  `district` int DEFAULT '0',
  `points` int DEFAULT NULL,
  `timestamp` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `patrols`
--

DROP TABLE IF EXISTS `patrols`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patrols` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patrol_name` char(225) DEFAULT NULL,
  `path` char(125) DEFAULT NULL,
  `people` int DEFAULT NULL,
  `time` time DEFAULT NULL,
  `fraction` int DEFAULT NULL,
  `phone` char(225) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `qr`
--

DROP TABLE IF EXISTS `qr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qr` (
  `id` varchar(12) NOT NULL,
  `type` varchar(45) DEFAULT NULL,
  `district` int DEFAULT NULL,
  `timestamp` varchar(45) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `organizer_name` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `results`
--

DROP TABLE IF EXISTS `results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `results` (
  `patrol_id` int NOT NULL,
  `patrol_name` char(255) DEFAULT NULL,
  `path` varchar(45) DEFAULT NULL,
  `fraction` int DEFAULT NULL,
  `points` int DEFAULT NULL,
  `time` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`patrol_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-10 13:33:53
