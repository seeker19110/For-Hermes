// ... (Previous code)
async function check() {
    console.log(`Checking Task: ${TASK_ID}`);
    const res = await request('DescribeTaskDetail', { 
        SubAppId: SUB_APP_ID, 
        TaskId: TASK_ID 
    });
    
    if (res.Response && res.Response.AigcVideoTask) {
        const task = res.Response.AigcVideoTask;
        console.log(`Status: ${task.Status}`);
        
        if (task.Status === 'FINISH') {
            // Check Output structure carefully
            if (task.Output && task.Output.FileInfos && task.Output.FileInfos.length > 0) {
                const file = task.Output.FileInfos[0];
                console.log(`Video URL: ${file.FileUrl}`);
            } else {
                console.log("Task Finished but Output is empty/invalid.");
                console.log(JSON.stringify(task.Output, null, 2));
            }
        } else if (task.Status === 'FAIL') {
             console.log(`Error: ${task.Message} (${task.ErrCodeExt})`);
        }
    } else {
        console.log(JSON.stringify(res, null, 2));
    }
}
check();
