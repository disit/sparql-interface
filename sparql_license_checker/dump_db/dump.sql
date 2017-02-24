-- MySQL dump 10.13  Distrib 5.7.11, for Linux (x86_64)
--
-- Host: localhost    Database: SiiMobility
-- ------------------------------------------------------
-- Server version	5.5.5-10.1.13-MariaDB

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
-- Table structure for table `lic_categories`
--

DROP TABLE IF EXISTS `lic_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lic_categories` (
  `CatId` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CatId`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lic_categories`
--

LOCK TABLES `lic_categories` WRITE;
/*!40000 ALTER TABLE `lic_categories` DISABLE KEYS */;
INSERT INTO `lic_categories` VALUES (1,'Cittadino'),(2,'Turista'),(3,'Polizia'),(4,'Carabinieri'),(5,'Protezione Civile'),(6,'Vigili del fuoco');
/*!40000 ALTER TABLE `lic_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lic_perm_cond`
--

DROP TABLE IF EXISTS `lic_perm_cond`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lic_perm_cond` (
  `PId` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(255) DEFAULT NULL,
  `duty` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`PId`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lic_perm_cond`
--

LOCK TABLES `lic_perm_cond` WRITE;
/*!40000 ALTER TABLE `lic_perm_cond` DISABLE KEYS */;
INSERT INTO `lic_perm_cond` VALUES (1,'derivative',0),(2,'sharealike',1),(3,'attribution',1),(4,'commecialize',0),(5,'redistribute',0),(6,'access-play',0),(7,'share',0);
/*!40000 ALTER TABLE `lic_perm_cond` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `licenses`
--

DROP TABLE IF EXISTS `licenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `licenses` (
  `LMId` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(255) DEFAULT NULL,
  `link` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`LMId`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licenses`
--

LOCK TABLES `licenses` WRITE;
/*!40000 ALTER TABLE `licenses` DISABLE KEYS */;
INSERT INTO `licenses` VALUES (1,'test',NULL),(2,'CC BY','https://creativecommons.org/licenses/by/2.0/it/'),(3,'CC BY Cittadino',NULL),(4,'CC BY NC','https://creativecommons.org/licenses/by-nc/2.0/it/'),(5,'CC BY NC SA','https://creativecommons.org/licenses/by-nc-sa/3.0/it/');
/*!40000 ALTER TABLE `licenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `licenses_categories`
--

DROP TABLE IF EXISTS `licenses_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `licenses_categories` (
  `LMId` int(11) NOT NULL,
  `CatId` int(11) DEFAULT NULL,
  KEY `LMID` (`LMId`),
  KEY `fk_l_c` (`CatId`),
  CONSTRAINT `LMID` FOREIGN KEY (`LMId`) REFERENCES `licenses` (`LMId`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_l_c` FOREIGN KEY (`CatId`) REFERENCES `lic_categories` (`CatId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licenses_categories`
--

LOCK TABLES `licenses_categories` WRITE;
/*!40000 ALTER TABLE `licenses_categories` DISABLE KEYS */;
INSERT INTO `licenses_categories` VALUES (1,1),(1,2),(2,3),(3,1);
/*!40000 ALTER TABLE `licenses_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `licenses_permcond`
--

DROP TABLE IF EXISTS `licenses_permcond`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `licenses_permcond` (
  `LMId` int(11) NOT NULL,
  `Pid` int(11) DEFAULT NULL,
  KEY `LMID2` (`LMId`),
  KEY `fk_l_p` (`Pid`),
  CONSTRAINT `LMID2` FOREIGN KEY (`LMId`) REFERENCES `licenses` (`LMId`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_l_p` FOREIGN KEY (`Pid`) REFERENCES `lic_perm_cond` (`PId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licenses_permcond`
--

LOCK TABLES `licenses_permcond` WRITE;
/*!40000 ALTER TABLE `licenses_permcond` DISABLE KEYS */;
INSERT INTO `licenses_permcond` VALUES (2,1),(2,3),(2,4),(2,5),(2,6),(2,7),(5,1),(5,2),(5,3),(5,5),(5,6),(5,7),(4,1),(4,3),(4,5),(4,6),(4,7);
/*!40000 ALTER TABLE `licenses_permcond` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `process_manager2`
--

DROP TABLE IF EXISTS `process_manager2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `process_manager2` (
  `process` varchar(300) CHARACTER SET latin1 NOT NULL,
  `Resource` varchar(300) CHARACTER SET latin1 DEFAULT NULL,
  `Resource_Class` varchar(300) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Category` varchar(300) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Format` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Automaticity` text CHARACTER SET latin1,
  `Process_type` text CHARACTER SET latin1,
  `Access` text CHARACTER SET latin1,
  `Real_time` varchar(5) COLLATE utf8_unicode_ci DEFAULT 'no',
  `Source` text CHARACTER SET latin1,
  `A` text CHARACTER SET latin1,
  `B` text CHARACTER SET latin1,
  `C` text COLLATE utf8_unicode_ci,
  `D` text COLLATE utf8_unicode_ci,
  `E` text COLLATE utf8_unicode_ci,
  `status_A` text CHARACTER SET latin1,
  `status_B` text CHARACTER SET latin1,
  `status_C` text CHARACTER SET latin1,
  `status_D` text COLLATE utf8_unicode_ci,
  `status_E` text COLLATE utf8_unicode_ci,
  `time_A` text CHARACTER SET latin1,
  `time_B` text CHARACTER SET latin1,
  `time_C` text CHARACTER SET latin1,
  `time_D` text COLLATE utf8_unicode_ci,
  `time_E` text COLLATE utf8_unicode_ci,
  `exec_A` varchar(5) CHARACTER SET latin1 DEFAULT 'no',
  `exec_B` text CHARACTER SET latin1,
  `exec_C` text CHARACTER SET latin1,
  `exec_D` text COLLATE utf8_unicode_ci,
  `exec_E` text COLLATE utf8_unicode_ci,
  `error_A` text COLLATE utf8_unicode_ci,
  `error_B` text COLLATE utf8_unicode_ci,
  `error_C` text COLLATE utf8_unicode_ci,
  `error_D` text COLLATE utf8_unicode_ci,
  `error_E` text COLLATE utf8_unicode_ci,
  `period` int(11) DEFAULT NULL,
  `overtime` int(11) DEFAULT NULL,
  `param` text CHARACTER SET latin1,
  `last_update` text CHARACTER SET latin1,
  `last_triples` text CHARACTER SET latin1,
  `Triples_count` int(11) DEFAULT NULL,
  `Triples_countRepository` int(11) DEFAULT NULL,
  `triples_insertDate` text COLLATE utf8_unicode_ci,
  `error` text CHARACTER SET latin1,
  `description` text CHARACTER SET latin1,
  `url_web_disit` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `SecurityLevel` int(1) NOT NULL DEFAULT '1',
  `LicenseUrl` text COLLATE utf8_unicode_ci NOT NULL,
  `LicenseText` longtext COLLATE utf8_unicode_ci NOT NULL,
  `LicenseModel` int(11) DEFAULT NULL,
  `startAt` int(11) DEFAULT NULL,
  PRIMARY KEY (`process`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-04-14 16:00:20
