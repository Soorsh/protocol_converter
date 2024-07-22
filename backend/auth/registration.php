<?php
    require_once $_SERVER['DOCUMENT_ROOT'] . '/config.php';

    $password = trim($_POST['password']);
    $confirmPassword = trim($_POST['confirmPassword']);
    if($password != $confirmPassword) exit("Пароли не совпадают");

    $email = trim($_POST['email']);

    $query = sprintf("SELECT * FROM `users` WHERE `email` = '%s'", $email);
    $rows = mysqli_query($db, $query);
    if ($rows->num_rows) exit("Пользователь существует");

    $firstName = trim($_POST['firstName']);
    $lastName = trim($_POST['lastName']);
    $patronymic = trim($_POST['patronymic']);

    $password = password_hash($password, PASSWORD_BCRYPT);

    $db->query("INSERT INTO `users` (`firstName`, `lastName`, `patronymic`, `email`, `password`) VALUES('$firstName', '$lastName', '$patronymic', '$email', '$password')");

    setcookie('user_id', $db->insert_id, time() + 3600 * 48, '/');

    $db->close();
?>
