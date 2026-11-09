package io.zershyan.examplemod.registry;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.command.ExampleCommand;
import net.minecraft.commands.CommandSourceStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.IEventBus;

import static net.minecraft.commands.Commands.literal;

public final class ExampleModCommands {
    private static final org.slf4j.Logger LOGGER = org.slf4j.LoggerFactory.getLogger(ExampleModCommands.class);

    private ExampleModCommands() {
    }

    public static void doRegister(IEventBus forgeBus, IEventBus modBus) {
        forgeBus.addListener(ExampleModCommands::commonCommandRegister);
    }

    public static void commonCommandRegister(RegisterCommandsEvent event) {
        LiteralArgumentBuilder<CommandSourceStack> builder = literal(ExampleMod.MODID);
        ExampleCommand.register(builder);
        event.getDispatcher().register(builder);
        LOGGER.debug("Registered /{} command", ExampleMod.MODID);
    }
}
