<?php
require_once '/var/www/html/config.php';
$dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
$pdo = new PDO($dsn, DB_USER, DB_PASS);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$packetData = fgets(STDIN);
processPacketData($packetData);
function processPacketData($packetData) {
    global $pdo;
    $data = json_decode($packetData, true);
    if (!isset($data["imei"]) || !isset($data["height"]) || !isset($data["fuel"])) {

    }
    $imei = $data["imei"];
    $height = (float)$data["height"];
    $fuel = (float)$data["fuel"];
    $heightStatus = $height == 0.0 ? 0 : 1;
    $fuelStatus = $fuel == 0.0 ? 0 : 1;
    $sqlUpdate = "INSERT INTO equipment_status (imei, data_sending, gps_status, fuel_status)
              VALUES (:imei, false, :height, :fuel)
              ON DUPLICATE KEY UPDATE data_sending = false, gps_status = :height, fuel_status = :fuel, last_update = CURRENT_TIMESTAMP";
    $stmt = $pdo->prepare($sqlUpdate);
    $stmt->execute([
        ':imei' => $imei,
        ':height' => $heightStatus,
        ':fuel' => $fuelStatus
    ]);
    $pdo = null;
}
?>