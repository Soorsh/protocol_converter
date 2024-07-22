<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';

$dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
$pdo = new PDO($dsn, DB_USER, DB_PASS);

$machineName = $_POST['machineName'];
$field1 = $_POST['field1'];
$field2 = $_POST['field2'];
$imei = $_POST['imei'];
$description = $_POST['description'];

$insertOrUpdateQuery = "INSERT INTO protocol_selection (machine_name, field_1, field_2, imei, description) VALUES (?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE field_1 = VALUES(field_1), field_2 = VALUES(field_2), imei = VALUES(imei), description = VALUES(description)";
$insertOrUpdateStatement = $pdo->prepare($insertOrUpdateQuery);
$insertOrUpdateStatement->execute([$machineName, $field1, $field2, $imei, $description]);

$response = [
    "success" => true,
    "message" => "Данные успешно сохранены!"
];
header('Content-Type: application/json');
echo json_encode($response);
?>
