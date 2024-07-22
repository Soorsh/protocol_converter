<?php

include 'config.php';

$title = !isset($_COOKIE['user_id']) ? "Аутентификация" : "Конвертер протоколов";

include 'header.php';

if(!isset($_COOKIE['user_id'])) {
    include 'pages/auth.html';
    $scriptName = "auth";
} else {
    include 'pages/main.php';
    $scriptName = "app";
}

include 'footer.php';

$db->close();

?>
