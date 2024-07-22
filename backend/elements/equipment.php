<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);


require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';

$query = "";
$organization_id = trim($_POST['organization_id']);
$title = trim($_POST['title']);
$position = (int) $_POST['position'] > 0 ? $_POST['position'] : "@max_position";

if($position != "@max_position")
    $query .= "UPDATE `equipments` SET `position` = `position` + 1 WHERE `organization_id` = $organization_id AND `position` >= $position;";
else $query .= "SET @max_position = (SELECT COUNT(*) FROM (SELECT * FROM `equipments` WHERE `organization_id` = $organization_id) AS organization_equipments) + 1;";
$query .= "INSERT INTO `equipments`(`organization_id`, `title`, `position`) VALUES ($organization_id, '$title', $position)";
print_r($query);
$db->multi_query($query);
