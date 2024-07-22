<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';

$email = trim($_POST['email']); // Получаем значение email из формы и очищаем его от нежелательных символов
$password = trim($_POST['password']); // Получаем значение пароля из формы и очищаем его от нежелательных символов

$query = sprintf("SELECT * FROM `users` WHERE `email` = '%s'", $email);

$rows = mysqli_query($db, $query);

if (!$rows->num_rows) exit("Пользователь не существует");

$user = mysqli_fetch_assoc($rows);

if (!$user || !password_verify($password, $user['password'])) exit("Пользователь не существует");

// Устанавливаем куки на 2 дня с информацией о пользователе
setcookie('user_id', $user['id'], time() + 3600 * 48, '/');

$db->close();
