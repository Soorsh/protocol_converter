<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';

$query = "";
$user_id = $_COOKIE['user_id'];
$title = trim($_POST['title']);
$position = (int) $_POST['position'] > 0 ? $_POST['position'] : "@max_position";

if($position != "@max_position") $query .= "UPDATE `organizations` SET `position` = `position` + 1 WHERE `position` >= $position;";
else $query .= "SET @max_position = (SELECT MAX(`position`) FROM `organizations`) + 1;";
$query .= "INSERT INTO `organizations` (`user_id`, `title`, `position`) VALUES ($user_id, '$title', $position);";
$db->multi_query($query);