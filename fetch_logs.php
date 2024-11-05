<?php
header('Content-Type: application/json');

// Database configuration
$host = 'localhost';
$db = 'cybersecurity_db';
$user = 'root';
$pass = '';

// Connect to the database
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch the latest logs
$sql = "SELECT timestamp, status, details FROM incidents ORDER BY timestamp DESC LIMIT 20";
$result = $conn->query($sql);

$logs = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $logs[] = $row;
    }
}

// Return logs as JSON
echo json_encode($logs);

$conn->close();
?>
