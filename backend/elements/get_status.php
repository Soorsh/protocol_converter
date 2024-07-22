<?php
require_once '/var/www/html/config.php';
$imei = $_GET['imei'];
$dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
$pdo = new PDO($dsn, DB_USER, DB_PASS);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$sql = "SELECT gps_status, fuel_status, data_sending, last_update FROM equipment_status WHERE imei = :imei";
$stmt = $pdo->prepare($sql);
$stmt->execute([':imei' => $imei]);

$data = $stmt->fetch(PDO::FETCH_ASSOC);

echo json_encode($data);
$pdo = null;
?>
