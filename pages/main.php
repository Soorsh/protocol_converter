<?php
    $organizations = [];
    $query = sprintf("
        SELECT 
            `organizations`.`id` as organization_id, 
            `organizations`.`title` as organization_title,
            `organizations`.`position` as organization_position,
            `equipments`.`id` as equipment_id,
            `equipments`.`title` as equipment_title,
            `equipments`.`position` as equipment_position
        FROM `organizations` 
        LEFT JOIN `equipments` ON
        `equipments`.`organization_id` = `organizations`.`id`
    ");
    $rows = $db->query($query);
    foreach ($rows as $row) {
        if(!isset($organizations[$row['organization_position']])) {
            $organizations += [
                $row['organization_position'] => [
                    'title' => $row['organization_title'],
                    'equipments' => [],
                    'id' => $row['organization_id']
                ]
            ];
        }

        $organization_equipments = $organizations[$row['organization_position']]['equipments'];
        if($row['equipment_position'] && !isset($organization_equipments[$row['equipment_position']])) {
            $organizations[$row['organization_position']]['equipments'] += [
                $row['equipment_position'] => [
                    'title' => $row['equipment_title'],
                    'id' => $row['equipment_id']
                ]
            ];
        }
    }
    ksort($organizations);
    foreach ($organizations as &$organization) {
        ksort($organization['equipments']);
    }
    unset($organization);
?>

<header>
    <div class="logo">
        <img src="/img/logo.png" alt="Логотип">
        <nav>
            <ul>
                <li><button class="header-button equipment">Техника</button></li>
            </ul>
        </nav>
    </div>
    <div class="header-right">
        <nav>
            <ul>
                <li><button id="logout">Выход</button></li>
            </ul>
        </nav>
    </div>
</header>

<main>
    <div class="organization-list_bar">
        <input type="text" id="search-input" placeholder="Поиск организаций и техники">
        <ul class="organization-list">
            <li id="add-element">Добавить...</li>
            <?php foreach($organizations as $organization): ?>
                <li id="organization-<?=$organization['id']?>" class="organization">
                    <div class="org-name-div">
                        <span class="toggle-button">+</span>
                        <label class="org-name"><?= $organization['title'] ?></label>
                    </div>
                    <ul class="equipment-list none">
                        <?php foreach($organization['equipments'] as $equipment): ?>
                            <li id="equipment-<?=$equipment['id']?>" class="equipment"><?= $equipment['title'] ?></li>
                        <?php endforeach; ?>
                    </ul>
                </li>
            <?php endforeach; ?>
        </ul>
    </div>

    <div class="sidebar">
        <div class="machine-tabs"></div>
        <div class="windows-info"></div>
    </div>
</main>
<div id="popup" class="none">
    <div class="popup-body">
        <h1>Создание</h1>
        <label>
            <select id="select-add-element">
                <option value="">Выберите элемент для создания</option>
                <option value="organization">Организация</option>
                <option value="equipment">Оборудование
            </select>
        </label>
        <form id="add-organization" class="none">
            <div class="inputs">
                <label>
                    <input type="text" name="title" maxlength="32" required>
                    <span>Наименование</span>
                </label>
                <label>
                    <input type="number" name="position" min="1" placeholder="В конец, если пусто">
                    <span>Позиция</span>
                </label>
                <div class="buttons">
                    <button type="submit">Добавить</button>
                </div>
            </div>
        </form>
        <form id="add-equipment" class="none">
            <div class="inputs">
                <label>
                    <select name="organization_id" required>
                        <option value="">Выберите организацию</option>
                        <?php foreach($organizations as $organization): ?>
                            <option value="<?=$organization['id']?>"><?=$organization['title']?></option>
                        <?php endforeach; ?>
                    </select>
                </label>
                <label>
                    <input type="text" name="title" maxlength="32" required>
                    <span>Наименование</span>
                </label>
                <label>
                    <input type="number" name="position" min="1" placeholder="В конец, если пусто">
                    <span>Позиция</span>
                </label>
                <div class="buttons">
                    <button type="submit">Добавить</button>
                </div>
            </div>
        </form>
    </div>
</div>
