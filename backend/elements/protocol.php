<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';
header('Content-Type: application/json');

$machineName = $_GET['machineName'] ?? '';

$query = "SELECT field_1, field_2, imei, description FROM protocol_selection WHERE machine_name = ?";
$statement = mysqli_prepare($db, $query);

mysqli_stmt_bind_param($statement, 's', $machineName);
mysqli_stmt_execute($statement);
mysqli_stmt_bind_result($statement, $field1, $field2, $imei, $description);

mysqli_stmt_fetch($statement);
echo json_encode(array('field_1' => $field1, 'field_2' => $field2, 'imei' => $imei, 'description' => $description));

mysqli_stmt_close($statement);
mysqli_close($db);
?>
