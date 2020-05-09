<?php
if (isset($_POST['submit'])) {
    $mailFrom = $_POST['mail'];
    $name = $_POST['name'];
    $subject= $_POST['subject'];
    $message = $_POST['message'];

    $mailTo ="deearavind@gmail.com";
    $headers = "From: ".$mailFrom;
    $txt = "You have recieved an email from".$name.".\n\n".$message;
    mail($mailTo, $subject, $txt, $headers);
    header("Location: index.php?mailsend");
}
?>