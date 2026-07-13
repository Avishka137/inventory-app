git add .                                                  
git commit -m "Updated it to read excel sheet using Uipath and automatically update the inventory."
git push origin main


<?php
$num = 1234;
$rev = 0;

while ($num > 0) {
    $digit = $num % 10;
    $rev = $rev * 10 + $digit;
    $num = (int)($num / 10);
}

echo "Reverse = " . $rev;
?>