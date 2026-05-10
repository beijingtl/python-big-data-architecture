/*
Source Server         : 192.168.0.54
Source Server Version : 50640
Source Host           : 192.168.0.54:3306
Source Database       : dwh

Target Server Type    : MYSQL
Target Server Version : 50640
File Encoding         : 65001

Date: 2021-06-23 14:15:31
*/

CREATE DATABASE dwh;
USE dwh;
DROP TABLE IF EXISTS `sku_info`;
CREATE TABLE `sku_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product` varchar(255) DEFAULT NULL,
  `price` decimal(12,4) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `stores` int(11) DEFAULT NULL,
  `cate` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
