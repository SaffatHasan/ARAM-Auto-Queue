export async function lcuProcessArgs() {
  return (await findLcuProcess()).cmd;
}

export async function findLcuProcess() {
  const process = await new Promise((resolve) =>
    Window.this.xcall('find_lcu_process', resolve)
  );
  return process || null;
}