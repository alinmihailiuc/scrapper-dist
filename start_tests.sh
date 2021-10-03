echo "#############################"
echo "STARTING TEST: ${TEST}"
echo "#############################"
cmd_tests="python3 -m pytest -n 4 --alluredir=./results -m ${TEST} --integration=${INTEGRATION}"
$cmd_tests
cmd_status=$?

cmd_after_tests="python3 after_tests.py"
$cmd_after_tests
cmd_after_tests=$?

if [ $cmd_status -eq 0 -a $cmd_after_tests -eq 0 ]
then
echo "Build success"
else
echo "Build failed"
exit 1
fi
