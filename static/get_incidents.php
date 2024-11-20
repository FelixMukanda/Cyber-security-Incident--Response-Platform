<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incidents</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <h1>Incidents</h1>
    <br>
    <table class="table">
        <thead>
            <tr>
                <th>Incident ID</th>
                <th>Incident Type</th>
                <th>Status</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            <?php
            $servername = "localhost"; 
            $username = "root"; 
            $password = ""; 
            $database = "cybersecurity_db";

            // Create connection
            $connection = new mysqli($servername, $username, $password, $database);

            // Check connection
            if ($connection->connect_error) {
                die("Connection failed: " . $connection->connect_error);
            }

            // Query to fetch incidents
            $sql = "SELECT * FROM incidents";
            $result = $connection->query($sql);

            // Check if query is successful
            if (!$result) {
                die("Invalid query: " . $connection->error);
            }

            // Fetch and display results
            while($row = $result->fetch_assoc()) {
                echo "<tr>
                    <td>" . $row["id"] . "</td>
                    <td>" . $row["incident_type"] . "</td>
                    <td>" . $row["status"] . "</td>
                    <td>" . $row["timestamp"] . "</td>
                </tr>";
            }

            // Close the database connection
            $connection->close();
            ?>
        </tbody>
    </table>
</body>
</html>
