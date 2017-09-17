-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema email_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema email_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `email_db` DEFAULT CHARACTER SET utf8 ;
USE `email_db` ;

-- -----------------------------------------------------
-- Table `email_db`.`emails`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `email_db`.`emails` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC))
ENGINE = InnoDB;

INSERT INTO emails (email, created_at, updated_at) VALUES("test@coding.com", NOW(), NOW());
INSERT INTO emails (email, created_at, updated_at) VALUES("jdoe@coding.com", NOW(), NOW());
INSERT INTO emails (email, created_at, updated_at) VALUES("fbar@coding.com", NOW(), NOW());

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

