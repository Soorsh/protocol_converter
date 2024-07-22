<?php
require_once "../config.php";
$dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
$pdo = new PDO($dsn, DB_USER, DB_PASS);

$packetData = fgets(STDIN);
processPacketData($packetData);

function processPacketData($packetData) {
    global $pdo;

    $data = json_decode($packetData, true);
    $imei = $data['imei'];

    $selectStatement = $pdo->prepare("SELECT field_2 FROM protocol_selection WHERE imei = ?");
    $selectStatement->execute([$imei]);
    $result = $selectStatement->fetch(PDO::FETCH_ASSOC);
    $serverName = $result['field_2'];

    $insertStatement = $pdo->prepare("INSERT INTO PacketLogs (imei, raw_data, server_name) VALUES (?, ?, ?)");
    $insertStatement->execute([$imei, $packetData, $serverName]);
}
?>
